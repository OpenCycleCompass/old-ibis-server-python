# Database Structure

## Tables

### TODO

* ~~add description to each table~~
* numeric data type precision


### Considerations

* Do not use *tokens*, instead let the user store his recorded *track ids*.
This is better data protection and tokens are not going to get used for special functions in future.
* Use *TEXT* for all columns containing strings.
See [this link](http://www.depesz.com/2010/03/02/charx-vs-varcharx-vs-varchar-vs-text/) for more information.
* time/timestamp is stored in PostgreSQL *timestamp* columns. 
*timestamp* columns provide 1 microsecond resolution, use 8 Byte and high value is 294276 AD.


#### *tracks*

Contains track metadata, hash of track points (*data_hash*) and bounding box

| Name  | Type | Description | foreign key |
|-------|------|-------------|-------------|
| **id** | bigserial | public track id | |
| created | timestamp | creation timestamp (send by device) | |
| uploaded | timestamp | upload timestamp (server-side evaluated) | |
| length | numeric(?) | length (in meter) fo track | |
| duration| bigint | duration (in milliseconds) of track | |
| num_points | bigint | number of points (coordinates) of track | |
| public | boolean | true if track is public visible | |
| name | text | track name | |
| comment | text | user's comment on track | |
| city | text | city where track starts (or ends?) | |
| data_hash |text | sha256 hash of track points (to remove duplicates) | |
| **bounding_box** | box2d | geometry box bounding track | |


#### *track_points*

This table contains the track points, ordered by track id from *tracks* table.

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

User table with user *name* (table index), sha256 hashed password, rights and enabled flag.

| Name  | Type | Description | foreign key |
|-------|------|-------------|-------------|
| iid | bigserial | table internal id | |
| **name** | text | unique user name | |
| password | text | hash (sha256?) of user password | |
| rights | bigint | user rights (0 is super user) | |
| enabled | boolean | true if user is enabled | |


#### *profiles*

This table contains one entry per Routing profile with an unique *id* and a name.

| Name  | Type | Description | foreign key |
|-------|------|-------------|-------------|
| **id** | bigserial | routing profile (unique) id | |
| name | text | name of routing profile | |


#### *profile_description*

Contains description(s in different languages) for every routing profile from *profiles* table.

| Name  | Type | Description | foreign key |
|-------|------|-------------|-------------|
| iid | bigserial | table internal id | |
| **id** | bigserial | routing profile id | [profiles](#profiles) -> id |
| language | text | profile description language | |
| description | text | profile description | |


#### *cost_static*

Static cost value are stored in this table.
For every way type from OSM and every routing profile a reverse and forward cost value is stored.

| Name  | Type | Description | foreign key |
|-------|------|-------------|-------------|
| iid | bigserial | table internal id | |
| **id** | bigint | *OSM* way type id (external) | ? |
| cost_forward | numeric(?) | forward cost for way type | |
| cost_reverse | numeric(?) | reverse cost for way type | |
| **profile** | bigserial | routing profile | [profiles](#profiles) -> id |


#### *cost_static_description*

Extended internationalized desciption for every OSM way type.

| Name  | Type | Description | foreign key |
|-------|------|-------------|-------------|
| **cost_static** | bigint | static cost way type id | [cost_static](#cost_static) -> id |
| name | text | name of way type | |
| description | text | description of way type | |
| language | text | language of way name and description | |


#### *cost_dynamic*

Dynamic cost value are stored in this table.
For each way segment in the local *pgRouting* database a reverse and forward cost value is stored.

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
