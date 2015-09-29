# Database Structure

## Tables

### TODO

* add description to each table
* ~~Precision of timestamps (64bit? / seconds or milliseconds)~~
* ~~character vs. varcharacter~~
* numeric data type precision


### Considerations

* Do not use *tokens*, instead let the user store his recorded *track ids*.
This is better data protection and tokens are not going to get used for special functions in future.
* Use *TEXT* for all columns containing strings.
See [this link](http://www.depesz.com/2010/03/02/charx-vs-varcharx-vs-varchar-vs-text/) for more information.
* time/timestamp is stored in PostgreSQL *timestamp* columns. 
*timestamp* columns provide 1 microsecond resolution, use 8 Byte and high value is 294276 AD.


#### *tracks*

| Name  | Type | Description | foreign key |
|-------|------|-------------|-------------|
| **id** | bigserial | public track id | |
| created | timestamp | creation timestamp (send by device) | |
| uploaded | timestamp | upload timestamp (server-side evaluated) | |
| length | numeric(?) | length (in meter) fo track | |
| duration| bigint | duration (in milliseconds) of track | |
| num_points | bigint | number of points (coordinates) of track | |
| public | boolean | true if track is public visible | |
| name | character(30) | track name | |
| comment | text | user's comment on track | |
| city | character(30) | city where track starts (or ends?) | |
| data_hash |character(64) | sha256 hash of track points (to remove duplicates) | |


#### *track_points*

| Name  | Type | Description | foreign key |
|-------|------|-------------|-------------|
| iid | bigserial | table internal id | |
| **id** | bigserial | track id | [tracks](#tracks) -> id |
| **geom** | geometry(POINT,4326) | coordinates of track point | |
| altitude | numeric(?) | optional altitude of track point | |
| accuracy | numeric(?) | optional accuracy of gps fix (in meter) | |
| time | timestamp | timestamp of track point | |
| velocity | numeric(?) | optional velocity at tracl point | |
| shock | numeric(?) | optional *shock* value to quantify street quality | |


#### *users*

| Name  | Type | Description | foreign key |
|-------|------|-------------|-------------|
| iid | bigserial | table internal id | |
| **name** | character(30) | unique user name | |
| password | character(64?) | hash (sha256?) of user password | |
| rights | bigint | user rights (0 is super user) | |


#### *profiles*

| Name  | Type | Description | foreign key |
|-------|------|-------------|-------------|
| **id** | bigserial | routing profile (unique) id | |
| name | character(30) | name of routing profile | |


#### *profile_description*

| Name  | Type | Description | foreign key |
|-------|------|-------------|-------------|
| iid | bigserial | table internal id | |
| **id** | bigserial | routing profile id | [profiles](#profiles) -> id |
| language | character(5) | profile description language | |
| description | text | profile description | |


#### *cost_static*

| Name  | Type | Description | foreign key |
|-------|------|-------------|-------------|
| iid | bigserial | table internal id | |
| **id** | bigint | *pgRouting* way type id (external) | ? |
| cost | numeric(?) | cost for way type | |
| profile | bigserial | routing profile | [profiles](#profiles) -> id |


#### *cost_static_description*

| Name  | Type | Description | foreign key |
|-------|------|-------------|-------------|
| **cost_static** | bigint | static cost way type id | [cost_static](#cost_static) -> id |
| name | character(30) | name of way type | |
| description | text | description of way type | |
| language | character(5) | language of way name and description | |


#### *cost_dynamic*

| Name  | Type | Description | foreign key |
|-------|------|-------------|-------------|
| iid | bigserial | table internal id | |
| **segment_id** | bigint | *pgRouting* segment id (external) | |
| track_id | bigserial | source of calculated dynamic cost | [tracks](#tracks) -> id |
| cost_forward | numeric(?) | forward cost for way segment | |
| cost_reverse | numeric(?) | reverse cost for way segment | |


#### *cost_dynamic_precalculated*

In table *cost_dynamic* for every way segment may exist more than 1 rows, so average of cost columns must be calculated.
In table *cost_dynamic_precalculated* the average cost values will be frequently calculated for each segment.

| Name  | Type | Description | foreign key |
|-------|------|-------------|-------------|
| iid | bigserial | table internal id | |
| **segment_id** | bigint | *pgRouting* segment id (external) | |
| cost_forward | numeric(?) | forward cost for way segment | |
| cost_reverse | numeric(?) | reverse cost for way segment | |

