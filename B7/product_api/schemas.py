from marshmallow import Schema, ValidationError, fields, validates, validate


class ProductIn(Schema):
    sku = fields.Str(required=True, validate=validate.Length(min=3, max=32))
    name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    description = fields.Str(allow_none=True, validate=validate.Length(max=2000))
    price_cents = fields.Int(required=True, strict=True, validate=validate.Range(min=0))
    qty_in_stock = fields.Int(load_default=0, strict=True, validate=validate.Range(min=0))

    @validates("sku", "name")
    def nonblank(self, value, **kwargs):
        if not value.strip():
            raise ValidationError("Khong duoc de trong.")


class ProductPatch(ProductIn):
    # partial=True in the route keeps absent fields unchanged, including defaults.
    pass


class ProductOut(Schema):
    id = fields.Int()
    sku = fields.Str()
    name = fields.Str()
    description = fields.Str(allow_none=True)
    price_cents = fields.Int()
    qty_in_stock = fields.Int()
    archived = fields.Bool()


class ReserveIn(Schema):
    qty = fields.Int(required=True, strict=True, validate=validate.Range(min=1))


class OrderItemIn(ReserveIn):
    product_id = fields.Int(required=True, strict=True, validate=validate.Range(min=1))


class OrderIn(Schema):
    customer_name = fields.Str(
        required=True, validate=[validate.Length(min=1, max=255), validate.Regexp(r"\S")]
    )
    items = fields.List(
        fields.Nested(OrderItemIn), required=True, validate=validate.Length(min=1)
    )
