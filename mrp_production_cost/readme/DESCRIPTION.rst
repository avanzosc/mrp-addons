This module extends the Manufacturing module to provide detailed cost tracking and estimation for Manufacturing Orders.

It adds the following cost fields to manufacturing orders:

- **Estimated Material Cost**: Sum of ``price_unit_cost * product_uom_qty`` for all raw material moves.
- **Real Material Cost**: Sum of ``price_unit_cost * quantity`` for all raw material moves.
- **Estimated Work Cost**: Sum of ``costs_hour * (duration_expected / 60)`` for all work orders.
- **Real Work Cost**: Sum of ``costs_hour * (duration / 60)`` for all work orders.
- **Estimated Manufacturing Cost**: Estimated Material Cost + Estimated Work Cost.
- **Real Manufacturing Cost**: Real Material Cost + Real Work Cost.
- **Cost Unit Price**: Real Manufacturing Cost divided by the produced quantity.

When a manufacturing order is marked as done, the real manufacturing cost is propagated to:

- The finished stock moves (unit cost).
- The production lot (purchase price), if applicable.
