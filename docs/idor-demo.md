# Idor-demo

| Call | Result |
| ---- | ------ |
| No token | **401** |
| GET, PATCH, DELETE, or clone of another user’s session | **404** `Session not found` |
| GET, PATCH, DELETE of another user’s plan, or attach using their plan | **404** `Plan not found` |
| GET, PATCH, DELETE of another user’s goal | **404** `Goal not found` |
| Attach their session onto your plan | **404** `Session not found` |
| `GET /sessions` or `GET /calendar` with their `plan_id` | **200** and an empty list |
| A random UUID | the same 404 detail as a real foreign id |

Status code 404 is used for both, missing and foreign ids, so that you can't know if id is in use or not.

## Before you start

Before installing, make sure you have following installed: 

###

- Node.js
- Docker
- Git
- Python 
- jq 
###

1. Copy .env.example to .env and copy frontend/.env.example to  frontend/.env
2. Run 
```bash
docker compose up --build
```
3. Run 
```bash
# First run this to migrate database.
docker compose exec api alembic upgrade head

# After migrating seed system units and activity types.
docker compose exec api python -m app.db.init_db
```
##
### 1. Creating users and logging in (store token)

First run these helpers: 
```bash
API=http://localhost:8000   # use your API_PORT from .env
JSON="Content-Type: application/json"

# Print the HTTP status after the body
req() { curl -s -w ' -> %{http_code}\n' "$@"; }
```

Registering returns `201`. Registering the same email again returns `400`, so use new emails on a rerun or reset the database.

### curl (bash, needs `jq`)

```bash
API=http://localhost:8000   # use your API_PORT from .env

#Creating users 
#User A, email: usera@testi.com and password is 'passowordA'
curl -s -X POST "$API/auth/register" \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"usera@testi.com\",\"password\":\"passwordA\",\"display_name\":\"User A\"}" > /dev/null

#User B, email: userb@testi.com and password is 'passowordB'
curl -s -X POST "$API/auth/register" \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"userb@testi.com\",\"password\":\"passwordB\",\"display_name\":\"User B\"}" > /dev/null

TOKEN_A=$(curl -s -X POST "$API/auth/login" -H "Content-Type: application/json" \
  -d '{"email":"usera@testi.com","password":"passwordA"}' | jq -r .access_token)
TOKEN_B=$(curl -s -X POST "$API/auth/login" -H "Content-Type: application/json" \
  -d '{"email":"userb@testi.com","password":"passwordB"}' | jq -r .access_token)

AUTH_A="Authorization: Bearer $TOKEN_A"
AUTH_B="Authorization: Bearer $TOKEN_B"

# Sanity check: should print User A, then User B
curl -s "$API/auth/me" -H "Authorization: Bearer $TOKEN_A" | jq -r .display_name
curl -s "$API/auth/me" -H "Authorization: Bearer $TOKEN_B" | jq -r .display_name
```


###
This should print:  
```bash
User A
User B
```

<br>

### 2. Creating a session, a plan and a goal as user A.

Look up the seeded Bench Press activity and its reps and weight units:

```bash
TYPES=$(curl -s "$API/activity-types" -H "$AUTH_A")
BENCH_ID=$(echo "$TYPES" | jq -r '.[] | select(.slug=="bench_press") | .id')
REPS_ID=$(echo "$TYPES"  | jq -r '.[] | select(.slug=="bench_press") | .unit_links[] | select(.unit_type.slug=="reps") | .unit_type_id')
KG_ID=$(echo "$TYPES"    | jq -r '.[] | select(.slug=="bench_press") | .unit_links[] | select(.unit_type.slug=="weight_kg") | .unit_type_id')
echo "BENCH_ID=$BENCH_ID REPS_ID=$REPS_ID KG_ID=$KG_ID"
```

All three must be numbers. If they are empty, the seed step was skipped.

Create the demo plan, the gym session with two bench press sets, and a weekly goal:

```bash
PLAN_A=$(curl -s -X POST "$API/plans" -H "$AUTH_A" -H "$JSON" \
  -d '{"name":"Demo strength plan","notes":"4-week strength block","length_weeks":4}' | jq -r .id)

SESSION_A=$(curl -s -X POST "$API/sessions" -H "$AUTH_A" -H "$JSON" -d @- <<EOF | jq -r .id
{
  "name": "Demo gym session: Chest day",
  "plan_id": $PLAN_A,
  "status": "planned",
  "notes": "Bench press, 2 sets",
  "items": [{
    "activity_type_id": $BENCH_ID,
    "sort_order": 0,
    "measurements": [
      {"unit_type_id": $REPS_ID, "planned_value": 8, "set_index": 0},
      {"unit_type_id": $KG_ID,   "planned_value": 60, "set_index": 0},
      {"unit_type_id": $REPS_ID, "planned_value": 8, "set_index": 1},
      {"unit_type_id": $KG_ID,   "planned_value": 60, "set_index": 1}
    ]
  }]
}
EOF
)

GOAL_A=$(curl -s -X POST "$API/goals" -H "$AUTH_A" -H "$JSON" \
  -d "{\"unit_type_id\":$REPS_ID,\"activity_type_id\":$BENCH_ID,\"target_value\":100,\"period\":\"week\"}" | jq -r .id)

echo "PLAN_A=$PLAN_A SESSION_A=$SESSION_A GOAL_A=$GOAL_A"
```

All three ids must be numbers. A `null` means that create call failed. Run it without `jq` to see the error.

A reads their own objects. Expected: **200** for each.

```bash
req "$API/sessions/$SESSION_A" -H "$AUTH_A"
req "$API/plans/$PLAN_A"       -H "$AUTH_A"
req "$API/goals/$GOAL_A"       -H "$AUTH_A"
```

<br>

### 3. As user B test to GET, PATCH and DELETE user A's session, pland and a goal.

No token. Expected: `{"detail":"Could not validate credentials"} -> 401`

```bash
req "$API/sessions/$SESSION_A"
```

A's session. Expected for each: `{"detail":"Session not found"} -> 404`

```bash
req           "$API/sessions/$SESSION_A"       -H "$AUTH_B"
req -X PATCH  "$API/sessions/$SESSION_A"       -H "$AUTH_B" -H "$JSON" -d '{"name":"hacked"}'
req -X DELETE "$API/sessions/$SESSION_A"       -H "$AUTH_B"
req -X POST   "$API/sessions/$SESSION_A/clone" -H "$AUTH_B"
```

A's plan. Expected for each: `{"detail":"Plan not found"} -> 404`

```bash
req           "$API/plans/$PLAN_A"                     -H "$AUTH_B"
req -X PATCH  "$API/plans/$PLAN_A"                     -H "$AUTH_B" -H "$JSON" -d '{"name":"hacked"}'
req -X DELETE "$API/plans/$PLAN_A"                     -H "$AUTH_B"
req -X POST   "$API/plans/$PLAN_A/sessions/$SESSION_B" -H "$AUTH_B"   # attach using their plan
```

A's goal. Expected for each: `{"detail":"Goal not found"} -> 404`

```bash
req           "$API/goals/$GOAL_A" -H "$AUTH_B"
req -X PATCH  "$API/goals/$GOAL_A" -H "$AUTH_B" -H "$JSON" -d '{"target_value":1}'
req -X DELETE "$API/goals/$GOAL_A" -H "$AUTH_B"
```

Attach A's session onto B's plan. Expected: `{"detail":"Session not found"} -> 404`

```bash
req -X POST "$API/plans/$PLAN_B/sessions/$SESSION_A" -H "$AUTH_B"
```

An id nobody owns. Expected: the same details as above, **404**.

```bash
req "$API/sessions/999999" -H "$AUTH_B"   # Session not found
req "$API/plans/999999"    -H "$AUTH_B"   # Plan not found
req "$API/goals/999999"    -H "$AUTH_B"   # Goal not found
```

Ids are integers. A UUID in the path returns 422, so use an unused integer.

### 4. As user B, try GET on all the sessions, plans, goals and calendar, should return empty rows.

Expected: only B's own rows (B session, B plan), and `[]` for goals.

```bash
req "$API/sessions" -H "$AUTH_B"
req "$API/plans"    -H "$AUTH_B"
req "$API/goals"    -H "$AUTH_B"
req "$API/calendar" -H "$AUTH_B"
```

Filtering by A's plan id. Expected: `[] -> 200`

```bash
req "$API/sessions?plan_id=$PLAN_A" -H "$AUTH_B"
req "$API/calendar?plan_id=$PLAN_A" -H "$AUTH_B"
```

### 5. Checking the user A's data is unchanged after user B's attemtps.

Expected: **200**, the session name is still `Demo gym session: Chest day`, and the plan and goal still exist.

```bash
req "$API/sessions/$SESSION_A" -H "$AUTH_A"
req "$API/plans/$PLAN_A"       -H "$AUTH_A"
req "$API/goals/$GOAL_A"       -H "$AUTH_A"
```