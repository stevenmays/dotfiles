// A queue consumer that claims each message in a table before it works.
// `step` models the current code, `stepDesign` the proposed lease design,
// and each `stepMut<Name>` removes one protection from the design.
module queue_consumer {
  pure val MESSAGES = Set("m1", "m2")
  // The queue moves a message to the dead-letter queue after 3 receives.
  pure val MAX_RECEIVES = 3
  // At-least-once delivery: allow 1 extra copy per message.
  pure val MAX_DUPLICATES = 1

  var visible: str -> int     // copies waiting in the queue
  var running: str -> int     // workers past the claim, per message; a count, so 2 owners show as 2
  var receives: str -> int
  var duplicates: str -> int
  var claim: str -> str       // claim row state: "none", "processing", or "done"
  var leaseLive: str -> bool  // design only: the claim's lease has not expired
  var completed: str -> int   // times the work committed
  var dlq: Set[str]

  action init = all {
    visible' = MESSAGES.mapBy(_ => 1),
    running' = MESSAGES.mapBy(_ => 0),
    receives' = MESSAGES.mapBy(_ => 0),
    duplicates' = MESSAGES.mapBy(_ => 0),
    claim' = MESSAGES.mapBy(_ => "none"),
    leaseLive' = MESSAGES.mapBy(_ => false),
    completed' = MESSAGES.mapBy(_ => 0),
    dlq' = Set(),
  }

  // Environment: the queue delivers an extra copy of a message.
  action duplicate(m) = all {
    duplicates.get(m) < MAX_DUPLICATES,
    visible' = visible.setBy(m, n => n + 1),
    duplicates' = duplicates.setBy(m, n => n + 1),
    running' = running, receives' = receives, claim' = claim,
    leaseLive' = leaseLive, completed' = completed, dlq' = dlq,
  }

  // Environment: the queue's redrive policy moves every waiting copy at once.
  action moveToDlq(m) = all {
    visible.get(m) > 0,
    receives.get(m) >= MAX_RECEIVES,
    visible' = visible.set(m, 0),
    dlq' = dlq.union(Set(m)),
    running' = running, receives' = receives, duplicates' = duplicates,
    claim' = claim, leaseLive' = leaseLive, completed' = completed,
  }

  // Current code: one INSERT ... ON CONFLICT DO NOTHING statement, so atomic.
  // A conflict counts as a duplicate, and the handler acks the copy.
  action receiveCurrent(m) = all {
    visible.get(m) > 0,
    receives.get(m) < MAX_RECEIVES,
    receives' = receives.setBy(m, n => n + 1),
    visible' = visible.setBy(m, n => n - 1),
    if (claim.get(m) == "none") all {
      claim' = claim.set(m, "processing"),
      running' = running.setBy(m, n => n + 1),
    } else all {
      claim' = claim,
      running' = running,
    },
    duplicates' = duplicates, leaseLive' = leaseLive, completed' = completed, dlq' = dlq,
  }

  // Design: one conditional write claims the row when its state is "none" or
  // its lease expired, and returns the row when the condition fails, so atomic.
  // A "done" row acks the copy. `onLiveLease` picks what a live lease does:
  // "retry" (the design) throws, so the queue redelivers the copy later.
  // "takeOver" and "ack" are mutants.
  action receiveDesign(m, onLiveLease) = all {
    visible.get(m) > 0,
    receives.get(m) < MAX_RECEIVES,
    receives' = receives.setBy(m, n => n + 1),
    val live = claim.get(m) == "processing" and leaseLive.get(m)
    if (claim.get(m) == "done" or (live and onLiveLease == "ack")) all {
      visible' = visible.setBy(m, n => n - 1),
      claim' = claim, running' = running, leaseLive' = leaseLive,
    } else if (live and onLiveLease == "retry") all {
      visible' = visible,
      claim' = claim, running' = running, leaseLive' = leaseLive,
    } else all {
      visible' = visible.setBy(m, n => n - 1),
      claim' = claim.set(m, "processing"),
      running' = running.setBy(m, n => n + 1),
      leaseLive' = leaseLive.set(m, true),
    },
    duplicates' = duplicates, completed' = completed, dlq' = dlq,
  }

  // Design: the lease is longer than the worker timeout, so a lease can
  // expire only after its owner has stopped.
  action expireLease(m) = all {
    claim.get(m) == "processing",
    leaseLive.get(m),
    running.get(m) == 0,
    leaseLive' = leaseLive.set(m, false),
    visible' = visible, running' = running, receives' = receives,
    duplicates' = duplicates, claim' = claim, completed' = completed, dlq' = dlq,
  }

  // One transaction writes the result and sets the claim to "done", so atomic.
  action finish(m) = all {
    running.get(m) > 0,
    running' = running.setBy(m, n => n - 1),
    completed' = completed.setBy(m, n => n + 1),
    claim' = claim.set(m, "done"),
    visible' = visible, receives' = receives, duplicates' = duplicates,
    leaseLive' = leaseLive, dlq' = dlq,
  }

  // Environment: the worker throws or hits its timeout before the commit.
  // Nothing releases the claim, and the queue makes the copy visible again.
  action crash(m) = all {
    running.get(m) > 0,
    running' = running.setBy(m, n => n - 1),
    visible' = visible.setBy(m, n => n + 1),
    receives' = receives, duplicates' = duplicates, claim' = claim,
    leaseLive' = leaseLive, completed' = completed, dlq' = dlq,
  }

  action step = {
    nondet m = MESSAGES.oneOf()
    any { receiveCurrent(m), finish(m), crash(m), duplicate(m), moveToDlq(m) }
  }

  action designWith(onLiveLease) = {
    nondet m = MESSAGES.oneOf()
    any { receiveDesign(m, onLiveLease), expireLease(m), finish(m), crash(m), duplicate(m), moveToDlq(m) }
  }

  action stepDesign = designWith("retry")
  // Removes the live-lease check: a copy takes over any "processing" claim.
  action stepMutNoLease = designWith("takeOver")
  // Removes the retry: a copy that sees a live lease is acked as a duplicate.
  action stepMutAckLiveLease = designWith("ack")

  // Every message is still queued, running, finished, or in the dead-letter queue.
  val noLostMessages = MESSAGES.forall(m =>
    visible.get(m) > 0 or running.get(m) > 0 or completed.get(m) > 0 or dlq.contains(m)
  )
  val atMostOnce = MESSAGES.forall(m => completed.get(m) <= 1)
  val oneOwner = MESSAGES.forall(m => running.get(m) <= 1)

  // Reachability witness: a crash leaves a claim with no running owner.
  val orphanClaim = MESSAGES.exists(m => claim.get(m) == "processing" and running.get(m) == 0)
  // Terminal witness: nothing is queued or running.
  val settled = MESSAGES.forall(m => visible.get(m) == 0 and running.get(m) == 0)
}
