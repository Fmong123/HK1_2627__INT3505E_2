from marshmallow import Schema, fields, validate


class ProductInSchema(Schema):
    sku = fields.String(
        required=True, validate=validate.Length(min=3, max=32),
        metadata={"example": "KB001"},
    )
    name = fields.String(
        required=True, validate=validate.Length(min=1, max=255),
        metadata={"example": "Bàn phím"},
    )
    price_cents = fields.Integer(
        strict=True, required=True, validate=validate.Range(min=0, max=2147483647),
        metadata={"example": 25000},
    )


class ProductSchema(ProductInSchema):
    id = fields.Integer(required=True, dump_only=True)
