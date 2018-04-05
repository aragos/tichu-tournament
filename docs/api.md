# tichu-tournament API

## Error Response

When responding with a 4xx or 5xx response code to any API call, the server should return error
information in this format instead of returning the normal response for that call.

    {
        "error": "Invalid name",
        "detail": "name must be non-empty"
    }

* `error`: The user-readable text of the error.
* `detail`: More specific text describing what exactly went wrong.

## Tournaments (/api/tournaments)

### List tournaments (GET /api/tournaments)

**Requires authentication.**
Retrieves the currently logged in director's tournament list.

#### Status codes

* **200**: Successfully listed tournaments.
* **401**: User is not logged in.
* **500**: Server failed to look up tournaments for any other reason.

#### Response

    {
        "tournaments": [{
            "id": "1234567890abcdef",
            "name": "Tournament Name"
        }]
    }

* `tournaments`: Array of objects. The list of tournaments owned by this user.
    * `id`: String. An opaque, unique ID used to access the details about this tournament.
    * `name`: String. A user-specified and user-readable name suitable for display in a tournament
      list.

### Create tournament (POST /api/tournaments)

**Requires authentication.**
Creates a new tournament owned by the currently logged in director.

#### Request

    {
        "name": "Tournament Name",
        "no_pairs": 8,
        "no_boards": 10,
        "players": [{
            "pair_no": 1,
            "name": "Michael the Magnificent",
            "email": "michael@michael.com"
        }]
    }

* `name`: String. A user-specified and user-readable name suitable for display in a tournament list.
  Required.
* `no_pairs`: Integer. The number of pairs (teams) to play in this tournament. Must be greater
  than 0. Required.
* `no_boards`: Integer. The number of boards (hands) to be played. Must be greater than 0.
  Required.
* `players`: List of objects. More information about the players. There should be at most
  two players for the same `pair_no`. Optional.
    * `pair_no`: Integer. The pair this player belongs to. Must be between 0 and `no_pairs`. Required.
    * `name`: String. User-readable name for the player. Optional.
    * `email`: String. Email for the player that can be used to identify user posting hand
      results. Optional.

#### Status codes

* **201**: The tournament was successfully created.
* **400**: One or more required fields were not specified, or failed validation.
* **401**: User is not logged in.
* **500**: Server failed to create a tournament for any other reason.
 
#### Response

    {
        "id": "1234567890abcdef"
    }

* `id`: String. An opaque, unique ID used to access the details about the newly created tournament.

### Read tournament (GET /api/tournaments/:id)

**Requires authentication and ownership of the given tournament.** 
Retrieves the details about a tournament owned by the currently logged in director.

#### Request

* `id`: String. An opaque, unique ID returned from `GET /tournaments` or `POST /tournaments`.

#### Status codes

* **200**: The tournament was successfully retrieved.
* **401**: User is not logged in.
* **403**: User is logged in, but does not own the given tournament.
* **404**: No tournament with the given ID exists.
* **500**: Server failed to locate the tournament for any other reason.

#### Response

    {
        "name": "Tournament Name",
        "no_pairs": 8,
        "no_boards": 10,
        "pair_ids": ["ABCD", "DEFG", "HIJK", "LMNO", "QRST", "UVWX", "YZAB", "CDEF"],
        "players": [{
            "pair_no": 1,
            "name": "Michael the Magnificent",
            "email": "michael@michael.com"
        }],
        "hands": [{
            "board_no": 3,
            "ns_pair": 4,
            "ew_pair": 6,
            "calls": {
                "north": "T",
                "east": "GT",
                "west": "",
                "south": ""
            },
            "ns_score": 150,
            "ew_score": -150,
            "notes": "hahahahahaha what a fool"
        }]
    }

* `name`: String. A user-specified and user-readable name suitable for display in a tournament list.
* `no_pairs`: Integer. The number of pairs (teams) to play in this tournament. Must be greater
  than 0. 
* `no_boards`: Integer. The number of boards (hands) to be played. Must be greater than 0.
* `pair_ids`: List of Strings. A list of unique ID codes associated with a team for
   this specific tournament. Length of the list must equal `no_pairs`.
* `players`: List of objects. More information about the players. There should be at most
  two players for the same `pair_no`. Optional.
    * `pair_no`: Integer. The pair this player belongs to. Must be between 0 and `no_pairs`. Required.
    * `name`: String. User-readable name for the player. Optional.
    * `email`: String. Email for the player that can be used to identify user posting hand
      results. Optional.
* `hands`: List of objects. The records of all hands played so far in this tournament. There will be
  at most one per combination of `board_no`, `ns_pair`, and `ew_pair`.
    * `board_no`: Integer. The board number for this hand. Must be between 1 and `no_boards`,
      inclusive.
    * `ns_pair`: Integer. The number of the north-south pair. Must be between 1 and `no_pairs`,
      inclusive, and different from `ew_pair`.
    * `ew_pair`: Integer. The number of the east-west pair. Must be between 1 and `no_pairs`,
      inclusive, and different from `ns_pair`.
    * `calls`: Object. Calls made by players. May have entries for `north`, `east`, `west`, `south`.
      Each entry may be `"T"`, indicating a call of Tichu, `"GT"`, indicating a call of Grand Tichu,
      or `""`, indicating no call. If an entry is absent, it is assumed to mean no call.
    * `ns_score`: Integer or string. The score of the north-south pair, including Tichu bonuses and
      penalties. May also be the string "AVG", "AVG+", "AVG++", "AVG-", or "AVG--".
    * `ew_score`: Integer or string. The score of the east-west pair, including Tichu bonuses and
      penalties. May also be the string "AVG", "AVG+", "AVG++", "AVG-", or "AVG--".
    * `notes`: String. Any additional notes about the hand added by the scorer or the director.

### Update tournament (PUT /api/tournaments/:id)

**Requires authentication and ownership of the given tournament.**
Updates the details about a tournament owned by the currently logged in director.

#### Request

* `id`: String. An opaque, unique ID returned from `GET /tournaments` or `POST /tournaments`.

<!-- time 4 code -->

    {
        "name": "Tournament Name",
        "no_pairs": 8,
        "no_boards": 10,
        "players": [{
            "pair_no": 1,
            "name": "Michael the Magnificent",
            "email": "michael@michael.com"
        }]
    }

* `name`: String. A user-specified and user-readable name suitable for display in a tournament list.
  Required.
* `no_pairs`: Integer. The number of pairs (teams) to play in this tournament. Must be greater
  than 0. Required.
  If `no_pairs` is different from the current setting of the tournament, the `pair_ids`
  associated with individual pairs are invalidated and new ones are recomputed. Otherwise
  the `pair_ids` stay the same even if `no_boards` or `name` is changed.
* `no_boards`: Integer. The number of boards (hands) to be played. Must be greater than 0.
  Required.
* `players`: List of objects. More information about the players. There should be at most
  two players for the same `pair_no`. Optional.
    * `pair_no`: Integer. The pair this player belongs to. Must be between 0 and `no_pairs`. Required.
    * `name`: String. User-readable name for the player. Optional.
    * `email`: String. Email for the player that can be used to identify user posting hand
      results. Optional.

#### Status codes

* **204**: The tournament was successfully updated.
* **400**: The tournament already has registered hand results.
* **401**: User is not logged in.
* **403**: User is logged in, but does not own the given tournament.
* **404**: No tournament with the given ID exists.
* **500**: Server failed to locate or update the tournament for any other reason.

### Delete tournament (DELETE /api/tournaments/:id)

**Requires authentication and ownership of the given tournament.**
Deletes a tournament owned by the currently logged in director.

#### Request

* `id`: String. An opaque, unique ID returned from `GET /tournaments` or `POST /tournaments`.

#### Status codes

* **204**: The tournament was successfully deleted.
* **401**: User is not logged in.
* **403**: User is logged in, but does not own the given tournament.
* **404**: No tournament with the given ID exists.
* **500**: Server failed to locate or delete the tournament for any other reason.

### Read hand preparation info (GET /api/tournaments/:id/handprep)

**Requires authentication and ownership of the given tournament.** 
Retrieves information about which teams should prepare which hands in the tournament.

#### Request

* `id`: String. An opaque, unique ID returned from `GET /tournaments` or `POST /tournaments`.

#### Status codes

* **200**: The hand preparation information was successfully retrieved.
* **401**: User is not logged in.
* **403**: User is logged in, but does not own the given tournament.
* **404**: No tournament with the given ID exists.
* **500**: Server failed to determine information for any other reason.

#### Response

    {
        "unplayed_hands": [
            {
                "pair_no": 1
                "hands": [1, 2, 5, 6]
            },
            {
                "pair_no": 2
                "hands": [1, 2, 5, 6]
            },
        ]
        "preparation": [
            {
                "pair_no": 1
                "hands": [1, 2]
            },
            {
                "pair_no": 2
                "hands": [5, 6]
            },
        ]
    }

* `unplayed_hands`: List of objects. Comprehensive information about which hands
  will not be played by each team. Required.
    * `pair_no`: Integer. The pair that has not played hands in this object. Required.
    * `hands`: List of Integers. List of all hands this pair will not play. Required.
* `preparation`: List of objects. Suggested set of hands each pair should prepare. Required.
    * `pair_no`: Integer. The pair that should prepare hands in this object. Required.
    * `hands`: List of Integers. List of all hands this pair should prepare. Required.

### Fetch the pair identifiers (GET /api/tournaments/:id/pairids)

**Requires authentication and ownership of the given tournament.**
Fetches the team unique identifiers for all pairs involved in the tournament.

#### Request

* `id`: String. An opaque, unique ID returned from `GET /tournaments` or `POST /tournaments`.

#### Status codes

* **200**: The pair ids were successfully retrieved.
* **401**: User is not logged in.
* **403**: User is logged in, but does not own the given tournament.
* **404**: No tournament with the given ID exists.
* **500**: Server failed to locate the ids for any other reason.

#### Response

    {
        "pair_ids": [ "ACJB", "DFKF", "ALRY", "DFRJ", "ADTR", "LKRN" ]
    }

* `pair_ids`: List of strings. A list of unique ID codes associated with a team for
   this specific tournament. Length of the list must equal `no_pairs` in the
   request. Stable as long as `num_pairs` does not change.

### Fetch a specific pair identifier (GET /api/tournaments/:id/pairids/:pair_no)

**Requires authentication and ownership of the given tournament.**
Fetches the team identifier for the pair number `pair_no`.

#### Request

* `id`: String. An opaque, unique ID returned from `GET /tournaments` or `POST /tournaments`.
* `pair_no`: Integer. The pair number.

#### Status codes

* **200**: The pair id was successfully retrieved.
* **401**: User is not logged in.
* **403**: User is logged in, but does not own the given tournament.
* **404**: No tournament with the given ID exists or the pair number is not a valid pair
  for this tournament.
* **500**: Server failed to locate the ids for any other reason.

#### Response

    {
        "pair_id": "ACJB"
    }

* `pair_id`: String. A unique ID code associated with this team for this specific tournament.
   Stable as long as `num_pairs` for the tournament does not change.

### Fetch a specific pair identifier (GET /api/tournaments/pairno/:pair_id)

Fetches the tournament information for the pair with `pair_id` identifier.

#### Request

* `pair_id`: String. The pair identifier.

#### Status codes

* **200**: The pair number was successfully retrieved.
* **404**: The pair ID does not exist.
* **500**: Server failed to locate the ids for any other reason.

#### Response

    {
        tournament_infos: [{
          "pair_no": 7
          "tournament_id": 1234567890abcdef
        }]
        
    }

* `tournament_infos`: List of objects. Each object contains information about an active tournament that
  pair is participating in. Will contain a single element almost always.
  * `pair_no`: Integer. The pair number associated with this ID in this tournament. Will be
     between 0 and the total number of pairs in the tournament.
  * `tournament_id`: String. Tournament id of this tournament.

### Get the schedule of boards a team must play. (GET /api/tournaments/:id/movement/:pair_no)

**Requires one of authentication and ownership of this tournament or a request
header with an appropriate pair id for pair_no**
Fetches the movement (schedule) for the team in question for this tournament.

#### Request Header
Optional. Necessary only for non-tournament owners.
<!-- time 4 code -->
    X-tichu-pair-code: MANQ

* `X-tichu-pair-code`: 4 character capitalized identifier of one of the pairs
  involved in this hand. This ID is the same as returned from 
  `GET /tournaments/:id/pairid/:pair_no`


#### Request

* `id`: String. An opaque, unique ID returned from `GET /tournaments` or `POST /tournaments`.
* `pair_no`: Integer. The team number for a pair in the tournament. Must be greater than
  0 and not higher than the number of pairs in the tournament.

#### Status codes

* **200**: The schedule was successfully retrieved.
* **404**: No tournament with the given ID exists or the pair number is invalid.
* **500**: Server failed to locate the schedule for any other reason.

#### Response

    {
        "name": "Tournament Name"
        "players": [{
            "name": "Michael the Magnificent",
            "email": "michael@michael.com"
        },
        {
            "name": "Anna the Amazing",
            "email": "anna@anna.com"
        }]
        "movement": [{
            "round": 1
            "position": "3N"
            "opponent": 2
            "opponent_names": [
                "Peter the Positive",
                "Christopher the Columbus"
            ]
            "hands": [
                {
                    "hand_no" : 13
                    "score" : {
                        "calls": {
                            "north": "T",
                            "east": "GT",
                            "west": "",
                            "south": ""
                         },
                        "ns_score": 150,
                        "ew_score": -150,
                        "notes": "I am a note"
                    },
                }
                {
                    "hand_no" : 14
                }
                {
                    "hand_no" : 15
                }
            ]
        },
        {
            "round": 2
            "position": "1E"
            "opponent": 4
            "opponent_names": [
                "Jonathan the Jovial",
                "Nathaniel the Notorious"
            ]
            "hands": [
                {
                    "hand_no" : 7
                }
                {
                    "hand_no" : 8
                }
                {
                    "hand_no" : 9
                }
        }
    ]
    }

* `name`: String. A user-specified and user-readable name suitable for display in a tournament list.
* `players`: List of objects. More information about the players. There should be at most
  two players.
    * `name`: String. User-readable name for the player. Optional.
    * `email`: String. Email for the player that can be used to identify user posting hand
      results. Optional.
* `movement`: List of objects. The generated movement that records all hands that this team
  plays along with associated opponents and position to be played from. An object for each
  round in the tournament will be included. If the pair requested did not play in the round
  only the `round` field will be populated.
    * `round`: Integer. The round number during which this hand is to be played. Required.
    * `position`: String. Position for this team. Two character string starting with the 
       table number and ending with either 'N' for North/South or 'E' for East/West. Optional.
    * `opponent`: Integer. The number of the opponent pair for this round. Required.
    * `opponent_names`: List of Strings. Names of the opponents for this round. Optional.
    * `hands`: List of integers. Set of hand numbers to be played by this team/opponent
       combination. Optional.
        * `score`: Object. If the hand has already been scored contains relevant information
          about the score. Optional.
          * `calls`: Object. Calls made by players. May have entries for `north`, `east`, `west`, `south`.
            Each entry may be `"T"`, indicating a call of Tichu, `"GT"`, indicating a call of Grand Tichu,
            or `""`, indicating no call. If an entry is absent, it is assumed to mean no call.
          * `ns_score`: Integer or string. The score of the north-south pair, including Tichu bonuses and
            penalties. May also be the string "AVG", "AVG+", "AVG++", "AVG-", or "AVG--".
          * `ew_score`: Integer or string. The score of the east-west pair, including Tichu bonuses and
            penalties. May also be the string "AVG", "AVG+", "AVG++", "AVG-", or "AVG--".
          * `notes`: String. Any additional notes about the hand added by the scorer or the director.
    * `relay_table`: Boolean. If set, this set of hands must be played simultaneously with
       another table. Optional.

### Check if hand has been scored (HEAD /api/tournaments/:id/hands/:board_no/:ns_pair/:ew_pair)

Checks if the given hand was already scored.

#### Request

* `id`: String. An opaque, unique ID returned from `GET /tournaments` or `POST /tournaments`.
* `board_no`: Integer. The board number for this hand. Must be between 1 and `no_boards`,
  inclusive.
* `ns_pair`: Integer. The number of the north-south pair. Must be between 1 and `no_pairs`,
  inclusive.
* `ew_pair`: Integer. The number of the east-west pair. Must be between 1 and `no_pairs`,
  inclusive.

#### Status codes

* **200**: The hand described by the URL exists.
* **204**: The hand does not exist, but the tournament does.
* **404**: The tournament with the given ID does not exist, or the board/pair numbers are invalid.
* **500**: Server failed to determine the hand's/tournament's existence (or lack thereof).

### Submit score for hand (PUT /api/tournaments/:id/hands/:board_no/:ns_pair/:ew_pair)

**Requires that the user is authenticated and owns this tournament or the request
header contain an appropriate pair id**, Submits a score for the given hand.

#### Request Header
Optional. Necessary only for overriding hand scores for non-tournament owners.
<!-- time 4 code -->
    X-tichu-pair-code: MANQ

* `X-tichu-pair-code`: 4 character capitalized identifier of one of the pairs
  involved in this hand. This ID is the same as returned from 
  `GET /tournaments/:id/pairid/:pair_no`

#### Request

* `id`: String. An opaque, unique ID returned from `GET /tournaments` or `POST /tournaments`.
* `board_no`: Integer. The board number for this hand. Must be between 1 and `no_boards`,
  inclusive.
* `ns_pair`: Integer. The number of the north-south pair. Must be between 1 and `no_pairs`,
  inclusive, and different from `ew_pair`.
* `ew_pair`: Integer. The number of the east-west pair. Must be between 1 and `no_pairs`,
  inclusive, and different from `ns_pair`.

<!-- time 4 code -->

    {
        "calls": {
            "north": "T",
            "east": "GT",
            "west": "",
            "south": ""
        },
        "ns_score": 150,
        "ew_score": -150,
        "notes": "hahahahahaha what a fool"
    }


* `calls`: Object. Calls made by players. May have entries for `north`, `east`, `west`, `south`.
  Each entry may be `"T"`, indicating a call of Tichu, `"GT"`, indicating a call of Grand Tichu,
  or `""`, indicating no call. If an entry is absent, it is assumed to mean no call. Required.
* `ns_score`: Integer or string. The score of the north-south pair, including Tichu bonuses and
  penalties. May also be the string "AVG", "AVG+", "AVG++", "AVG-", or "AVG--". Required.
* `ew_score`: Integer or string. The score of the east-west pair, including Tichu bonuses and
  penalties. May also be the string "AVG", "AVG+", "AVG++", "AVG-", or "AVG--". Required.
* `notes`: String. Any additional notes about the hand added by the scorer or the director.
  Required.

#### Status codes

* **204**: The hand has been scored.
* **400**: Validation failed for one or more of the fields in the score.
* **403**: The user does not own this tournament is not logged in and the request was not authenticate
  with the right pair id.
* **404**: The tournament with the given ID does not exist, the board/pair numbers are invalid
  or the pairs are not scheduled to play this board in the tournament movement scheme.
* **500**: Server failed to score the hand for any other reason.

### Delete score for hand (DELETE /api/tournaments/:id/hands/:board_no/:ns_pair/:ew_pair)

**Requires authentication and ownership of the given tournament.**
Deletes the score for the given hand from the server, allowing it to be scored again.

#### Request

* `id`: String. An opaque, unique ID returned from `GET /tournaments` or `POST /tournaments`.
* `board_no`: Integer. The board number for this hand. Must be between 1 and `no_boards`,
  inclusive.
* `ns_pair`: Integer. The number of the north-south pair. Must be between 1 and `no_pairs`,
  inclusive, and different from `ew_pair`.
* `ew_pair`: Integer. The number of the east-west pair. Must be between 1 and `no_pairs`,
  inclusive, and different from `ns_pair`.

#### Status codes

* **204**: The score for the hand has been erased.
* **401**: User is not logged in.
* **403**: The user is logged in, but does not own this tournament.
* **404**: The tournament with the given ID does not exist, or the board/pair numbers are invalid.
* **500**: Server failed to delete the hand for any other reason.

### Get change log for a hand (GET /api/tournaments/:id/hands/changelog/:board_no/:ns_pair/:ew_pair)

**Requires authentication and ownership of the given tournament.**
Gets a complete change log for a specific hand.

#### Request

* `id`: String. An opaque, unique ID returned from `GET /tournaments` or `POST /tournaments`.
* `board_no`: Integer. The board number for this hand. Must be between 1 and `no_boards`,
  inclusive.
* `ns_pair`: Integer. The number of the north-south pair. Must be between 1 and `no_pairs`,
  inclusive, and different from `ew_pair`.
* `ew_pair`: Integer. The number of the east-west pair. Must be between 1 and `no_pairs`,
  inclusive, and different from `ns_pair`.

<!-- time 4 code -->

    {
        "changes": [
            {
                "change": {
                    "calls": {
                        "north": "", 
                        "south": "T", 
                        "west": "", 
                        "east": ""
                    }, 
                    "ew_score": 20, 
                    "ns_score": 180
                }, 
                "timestamp_sec": "1482804837.85", 
                "changed_by": 1
            }, 
            {
                "change": {
                    "ns_score": 180, 
                    "calls": {
                        "north": "", 
                        "south": "T", 
                        "west": "", 
                        "east": ""
                    }, 
                    "ew_score": 20, 
                    "notes" : "Hello there"
                }, 
                "timestamp_sec": "1482804384.03", 
                "changed_by": 1
            }
        ]
    }

* `changes` : List of objects. Every change made to the score ordered in reverse 
  timestamp order. Deletions are have all empty fields except `timestamp_sec`. May be empty
  if the hand was never scored.
  * `change`: Object. The change made at a given time. Required.
    * `calls`: Object. Calls made by players. May have entries for `north`, `east`, `west`, `south`.
      Each entry may be `"T"`, indicating a call of Tichu, `"GT"`, indicating a call of Grand Tichu,
      or `""`, indicating no call. If an entry is absent, it is assumed to mean no call. Must be null
      or not present for a hand deletion change. Optional.
    * `ns_score`: Integer or string. The score of the north-south pair, including Tichu bonuses and
      penalties. May also be the string "AVG", "AVG+", "AVG++", "AVG-", or "AVG--". Must be null or
      not present for a hand deletion change. Required.
    * `ew_score`: Integer or string. The score of the east-west pair, including Tichu bonuses and
      penalties. May also be the string "AVG", "AVG+", "AVG++", "AVG-", or "AVG--". Must be null 
      or not present for a hand deletion change. Required.
    * `notes`: String. Any additional notes about the hand added by the scorer or the director.
      Must be null or not present for a hand deletion change. Required.
  * `timestamp_sec`: Float. Time in seconds from epoch when the change was made. Required.
  * `changed_by`: Integer. Pair number of the team that made the change. If 0, change was made
    by the director. Required.

#### Status codes

* **204**: The change log was successfully fetched.
* **403**: The user does not own this tournament or is not logged in.
* **404**: The tournament with the given ID does not exist, the board/pair numbers are invalid
  or the pairs are not scheduled to play this board in the tournament movement scheme.
* **500**: Server failed to score the hand for any other reason.

### Check hands that have not been scored yet (GET /api/tournaments/:id/unscoredHands)

**Requires authentication and ownership of the given tournament.**
Checks if all the hands to be played in this tournament have been scored and returns
all hands not yet scored.

#### Request

* `id`: String. An opaque, unique ID returned from `GET /tournaments` or `POST /tournaments`.

#### Status Codes
* **200**: The unscored hands have been returned. 
* **401**: User is not logged in.
* **403**: The user is logged in, but does not own this tournament.
* **404**: The tournament with the given ID does not exist.
* **500**: Server failed to generate the list of unscored hands for any other reason.

#### Response

    {
        "unscored_hands": [
            {
                "hand": 9, 
                "ew_pair": 2, 
                "ns_pair": 1
            }
        ]
    }

* `unscored_hands`: List of objects. Each object is a hand that has not been scored yet.
  * `hand`: Integer. Number of the hand that hasn't been scored yet. Must be between 1
    and the number of hands in the tournament configuration.
  * `ew_pair`: Integer. Number of the East/West pair in this matchup. Must be between 1
    and the number of pairs in the tournament configuration.
  * `ns_pair`: Integer. Number of the North/South pair in this matchup. Must be between 1
    and the number of pairs in the tournament configuration.

### Generate final score (GET /api/tournaments/:id/results)

**Requires authentication and ownership of the given tournament.**
Calculates and returns the final detailed results of the tournament.

#### Request

* `id`: String. An opaque, unique ID returned from `GET /tournaments` or `POST /tournaments`.

#### Status codes

* **200**: The score has been generated.
* **401**: User is not logged in.
* **403**: The user is logged in, but does not own this tournament.
* **404**: The tournament with the given ID does not exist.
* **500**: Server failed to generate the score for any other reason.

#### Response

    {
        "pair_summaries": [{
            "pair_no": 3,
            "mps": 50,
            "rps": 90
            "aps": 90
        }],
        "hands": [{
            "board_no": 3,
            "ns_pair": 4,
            "ew_pair": 6,
            "calls": {
                "north": "T",
                "east": "GT",
                "west": "",
                "south": ""
            },
            "ns_score": 150,
            "ew_score": -150,
            "ns_mps": 60,
            "ew_mps": 20,
            "ns_rps": 30,
            "ew_rps": 40,
            "ns_aps": 5
            "ew_aps": 2
            "notes": "hahahahahaha what a fool"
        }]
    }
    
* `pair_summaries`: List of objects. The summary of results for all pairs playing in this
  tournament. There will be exactly one for each pair between 1 and `no_pairs`.
    * `pair_no`: Integer. The number of the pair this summary is for.
    * `mps`: Float. The total number of match points scored by this pair in the tournament.
    * `rps`: Float. The total number of RPs scored by this pair in the tournament.
    * `aps`: Float. The total number of APs scored by this pair in the tournament.
* `hands`: List of objects. The final records of all hands played in this tournament. There will be
  at most one per combination of `board_no`, `ns_pair`, and `ew_pair`.
    * `board_no`: Integer. The board number for this hand. Must be between 1 and `no_boards`,
      inclusive.
    * `ns_pair`: Integer. The number of the north-south pair. Must be between 1 and `no_pairs`,
      inclusive, and different from `ew_pair`.
    * `ew_pair`: Integer. The number of the east-west pair. Must be between 1 and `no_pairs`,
      inclusive, and different from `ns_pair`.
    * `calls`: Object. Calls made by players. May have entries for `north`, `east`, `west`, `south`.
      Each entry may be `"T"`, indicating a call of Tichu, `"GT"`, indicating a call of Grand Tichu,
      or `""`, indicating no call. If an entry is absent, it is assumed to mean no call.
    * `ns_score`: Integer or string. The score of the north-south pair, including Tichu bonuses and
      penalties. May also be the string "AVG", "AVG+", "AVG++", "AVG-", or "AVG--".
    * `ew_score`: Integer or string. The score of the east-west pair, including Tichu bonuses and
      penalties. May also be the string "AVG", "AVG+", "AVG++", "AVG-", or "AVG--".
    * `ns_mps`: Float. The number of match points scored by the north-south pair in this hand.
    * `ew_mps`: Float. The number of match points scored by the east-west pair in this hand.
    * `ns_mps`: Float. The number of RPs scored by the north-south pair in this hand.
    * `ew_mps`: Float. The number of RPs scored by the east-west pair in this hand.  
    * `ns_aps`: Float. The number of APs scored by the north-south pair in this hand.
    * `ew_aps`: Float. The number of APs scored by the east-west pair in this hand.  
    * `notes`: String. Any additional notes about the hand added by the scorer or the director.

### Generate final score in XLSX format (GET /api/tournaments/:id/xlsresults)

**Requires authentication and ownership of the given tournament.**
Calculates and returns the final detailed results of the tournament as a .xlsx file.

#### Request

* `id`: String. An opaque, unique ID returned from `GET /tournaments` or `POST /tournaments`.

#### Status codes

* **200**: The score has been generated.
* **401**: User is not logged in.
* **403**: The user is logged in, but does not own this tournament.
* **404**: The tournament with the given ID does not exist.
* **500**: Server failed to generate the score for any other reason.

#### Response
.xlsx file with all the results.