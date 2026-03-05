# Data Quality Report
## Dataset summary
| Metric | Value |
|---|---|
| Total events | 1584 |

## Missing fields
| Field | Missing | Rate |
|---|---:|---:|
| postal_code | 35 | 0.0221 |
| title | 0 | 0.0000 |
| description | 0 | 0.0000 |
| start_datetime | 0 | 0.0000 |
| city | 0 | 0.0000 |
| lat | 0 | 0.0000 |
| lon | 0 | 0.0000 |
| url | 0 | 0.0000 |

## Date validation
| Metric | Value |
|---|---|
| Invalid dates | 1 |
| Rate | 0.0006 |
| Window (UTC) | 2025-03-05T15:42:04.437874+00:00 → 2027-03-05T15:42:04.437874+00:00 |

## Geographic validation
| Metric | Value |
|---|---|
| Inconsistent geo | 100 |
| Rate | 0.0631 |

### Geo details
| Check | Count |
|---|---:|
| dept_not_34 | 0 |
| bbox_outside | 100 |
| geo_parse_error | 0 |

### BBox
| Param | Value |
|---|---|
| lat_min | 43.1 |
| lat_max | 43.8 |
| lon_min | 2.0 |
| lon_max | 4.0 |
