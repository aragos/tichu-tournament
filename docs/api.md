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
      penalties. May also be the string "AVG+" or "AVG-".
    * `ew_score`: Integer or string. The score of the east-west pair, including Tichu bonuses and
      penalties. May also be the string "AVG+" or "AVG-".
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
* `no_boards`: Integer. The number of boards (hands) to be played. Must be greater than 0.
  Required.

#### Status codes

* **204**: The tournament was successfully updated.
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

Submits a score for the given hand.
Or, **if the user is authenticated and owns this tournament**, updates an already submitted score.

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
  penalties. May also be the string "AVG+" or "AVG-". Required.
* `ew_score`: Integer or string. The score of the east-west pair, including Tichu bonuses and
  penalties. May also be the string "AVG+" or "AVG-". Required.
* `notes`: String. Any additional notes about the hand added by the scorer or the director.
  Required.

#### Status codes

* **204**: The hand has been scored.
* **400**: Validation failed for one or more of the fields in the score.
* **403**: The score for this hand has already been submitted, and the user does not own this
  tournament or is not logged in.
* **404**: The tournament with the given ID does not exist, or the board/pair numbers are invalid.
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
            "notes": "hahahahahaha what a fool"
        }]
    }
    
* `pair_summaries`: List of objects. The summary of results for all pairs playing in this
  tournament. There will be exactly one for each pair between 1 and `no_pairs`.
    * `pair_no`: Integer. The number of the pair this summary is for.
    * `mps`: Integer. The total number of match points scored by this pair in the tournament.
    * `rps`: Integer. The total number of RPs scored by this pair in the tournament.
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
      penalties. May also be the string "AVG+" or "AVG-".
    * `ew_score`: Integer or string. The score of the east-west pair, including Tichu bonuses and
      penalties. May also be the string "AVG+" or "AVG-".
    * `ns_mps`: Integer. The number of match points scored by the north-south pair in this hand.
    * `ew_mps`: Integer. The number of match points scored by the east-west pair in this hand.
    * `ns_mps`: Integer. The number of RPs scored by the north-south pair in this hand.
    * `ew_mps`: Integer. The number of RPs scored by the east-west pair in this hand.  
    * `notes`: String. Any additional notes about the hand added by the scorer or the director.
