from cryspy import unit1_test as u1


def test_unit1_test_data():
    assert len(u1.toy_source()) == 100000
    assert len(set(u1.toy_source())) == 16
    assert len(u1.ciphertext()) == 600
    assert all(0 <= b < 256 for b in u1.affine_ciphertext())
    assert all(0 <= b < 65537 for b in u1.power_ciphertext())


def test_generate_reproduces_source():
    assert u1.generate(100000, seed=4242) == u1.toy_source()
    assert set(u1.generate(5000, seed=1)) <= set(u1.toy_source())
