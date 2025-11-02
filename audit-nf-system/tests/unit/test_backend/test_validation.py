import pytest
from backend.validation.validator import validate_cnpj, validate_access_key, validate_cfop, calculate_icms

@pytest.mark.parametrize("cnpj,expected", [
    ("12345678000190", True),
    ("12345678000191", False),
    ("123", False),
])
def test_validate_cnpj(cnpj, expected):
    assert validate_cnpj(cnpj) == expected

@pytest.mark.parametrize("key,valid", [
    ("NFe12345678901234567890123456789012345678901234", True),
    ("short", False),
])
def test_validate_access_key(key, valid):
    assert validate_access_key(key) == valid

@pytest.mark.parametrize("cfop,expected", [
    ("5102", True),
    ("0000", False),
])
def test_validate_cfop(cfop, expected):
    assert validate_cfop(cfop) == expected

@pytest.mark.parametrize("base,aliquota,expected", [
    (1000.0, 0.18, 180.0),
    (200.0, 0.12, 24.0),
])
def test_calculate_icms(base, aliquota, expected):
    assert calculate_icms(base, aliquota) == pytest.approx(expected, rel=1e-6)
