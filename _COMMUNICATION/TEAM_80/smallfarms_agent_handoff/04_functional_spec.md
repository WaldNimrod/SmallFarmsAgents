# Functional Specification

## Entities

### Crop
- id
- name
- unit

### CostModel
- crop_id
- labor_cost
- water_cost
- seeds_cost
- land_cost
- misc_cost
- yield

### Calculation
- total_cost
- cost_per_unit
- recommended_price

## Logic

total_cost = sum(costs)
cost_per_unit = total_cost / yield
recommended_price = cost_per_unit * margin

## Modes
- Community mode (read)
- User edit mode

## Phase 1 Constraints
- No auth
- Optional save (future)
