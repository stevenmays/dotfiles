# A queue consumer that claims each message in a table before it works.
# `step` models the current code, `stepDesign` the proposed lease design,
# and each `stepMut<Name>` removes one protection from the design.
# This file models the same flow as `example-queue-consumer.qnt`.

MESSAGES = ["m1", "m2"]
# The queue moves a message to the dead-letter queue after 3 receives.
MAX_RECEIVES = 3
# At-least-once delivery: allow 1 extra copy per message.
MAX_DUPLICATES = 1


def init():
    return {
        "visible": {m: 1 for m in MESSAGES},      # copies waiting in the queue
        "running": {m: 0 for m in MESSAGES},      # workers past the claim; a count, so 2 owners show as 2
        "receives": {m: 0 for m in MESSAGES},
        "duplicates": {m: 0 for m in MESSAGES},
        "claim": {m: "none" for m in MESSAGES},   # claim row state: "none", "processing", or "done"
        "leaseLive": {m: False for m in MESSAGES},  # design only: the claim's lease has not expired
        "completed": {m: 0 for m in MESSAGES},    # times the work committed
        "dlq": set(),
    }


# Environment: the queue delivers an extra copy of a message.
def duplicate(s, m):
    if s["duplicates"][m] >= MAX_DUPLICATES:
        return False
    s["visible"][m] += 1
    s["duplicates"][m] += 1


# Environment: the queue's redrive policy moves every waiting copy at once.
def moveToDlq(s, m):
    if s["visible"][m] == 0 or s["receives"][m] < MAX_RECEIVES:
        return False
    s["visible"][m] = 0
    s["dlq"].add(m)


# Current code: one INSERT ... ON CONFLICT DO NOTHING statement, so atomic.
# A conflict counts as a duplicate, and the handler acks the copy.
def receiveCurrent(s, m):
    if s["visible"][m] == 0 or s["receives"][m] >= MAX_RECEIVES:
        return False
    s["receives"][m] += 1
    s["visible"][m] -= 1
    if s["claim"][m] == "none":
        s["claim"][m] = "processing"
        s["running"][m] += 1


# Design: one conditional write claims the row when its state is "none" or
# its lease expired, and returns the row when the condition fails, so atomic.
# A "done" row acks the copy. `onLiveLease` picks what a live lease does:
# "retry" (the design) throws, so the queue redelivers the copy later.
# "takeOver" and "ack" are mutants.
def receiveDesign(s, m, onLiveLease):
    if s["visible"][m] == 0 or s["receives"][m] >= MAX_RECEIVES:
        return False
    s["receives"][m] += 1
    live = s["claim"][m] == "processing" and s["leaseLive"][m]
    if s["claim"][m] == "done" or (live and onLiveLease == "ack"):
        s["visible"][m] -= 1
    elif live and onLiveLease == "retry":
        pass
    else:
        s["visible"][m] -= 1
        s["claim"][m] = "processing"
        s["running"][m] += 1
        s["leaseLive"][m] = True


# Design: the lease is longer than the worker timeout, so a lease can
# expire only after its owner has stopped.
def expireLease(s, m):
    if s["claim"][m] != "processing" or not s["leaseLive"][m] or s["running"][m] != 0:
        return False
    s["leaseLive"][m] = False


# One transaction writes the result and sets the claim to "done", so atomic.
def finish(s, m):
    if s["running"][m] == 0:
        return False
    s["running"][m] -= 1
    s["completed"][m] += 1
    s["claim"][m] = "done"


# Environment: the worker throws or hits its timeout before the commit.
# Nothing releases the claim, and the queue makes the copy visible again.
def crash(s, m):
    if s["running"][m] == 0:
        return False
    s["running"][m] -= 1
    s["visible"][m] += 1


SHARED = [(action, m) for m in MESSAGES for action in (finish, crash, duplicate, moveToDlq)]


def designWith(onLiveLease):
    return [(receiveDesign, m, onLiveLease) for m in MESSAGES] + [(expireLease, m) for m in MESSAGES] + SHARED


step = [(receiveCurrent, m) for m in MESSAGES] + SHARED
stepDesign = designWith("retry")
# Removes the live-lease check: a copy takes over any "processing" claim.
stepMutNoLease = designWith("takeOver")
# Removes the retry: a copy that sees a live lease is acked as a duplicate.
stepMutAckLiveLease = designWith("ack")


# Every message is still queued, running, finished, or in the dead-letter queue.
def noLostMessages(s):
    return all(s["visible"][m] > 0 or s["running"][m] > 0 or s["completed"][m] > 0 or m in s["dlq"] for m in MESSAGES)


def atMostOnce(s):
    return all(s["completed"][m] <= 1 for m in MESSAGES)


def oneOwner(s):
    return all(s["running"][m] <= 1 for m in MESSAGES)


# Reachability witness: a crash leaves a claim with no running owner.
def orphanClaim(s):
    return any(s["claim"][m] == "processing" and s["running"][m] == 0 for m in MESSAGES)


# Terminal witness: nothing is queued or running.
def settled(s):
    return all(s["visible"][m] == 0 and s["running"][m] == 0 for m in MESSAGES)
