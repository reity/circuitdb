"""
Data set of optimal circuits for Boolean functions that have
specific low arities.
"""
from __future__ import annotations
import doctest
import os
import math
import base64
import bitlist
import logical
import circuit

# The private dictionary that represents the data set.
class _db(dict):
    """
    Wrapper class for a circuit data set instance.
    """
    _data = {}

class record(bytes):
    """
    Wrapper class for an individual record (*i.e.*, encoded data corresponding to a
    circuit).
    """
    @staticmethod
    def from_circuit(circuit: circuit.circuit) -> record: # pylint: disable=W0621
        """
        Encode a :obj:`~circuit.circuit.circuit` object and construct a record that
        represents it.

        >>> c = circuit.circuit()
        >>> g0 = c.gate(logical.id_, is_input=True)
        >>> g1 = c.gate(logical.id_, is_input=True)
        >>> g2 = c.gate(logical.id_, is_input=True)
        >>> g3 = c.gate(logical.xor_, [g0, g2])
        >>> g4 = c.gate(logical.nimp_, [g1, g3])
        >>> g5 = c.gate(logical.id_, [g4], is_output=True)
        >>> record.from_circuit(c).to_base64()
        'CQACBAEDBgQ='
        """
        # Create table for converting an encoded operator into an actual operator value.
        integer_to_operator = list(sorted(list(logical.every)))

        # Convert gate data into a list of integers. Note that the number of gates
        # (including input and output gates) must not exceed 256.
        bs = []
        for g in circuit.gate:
            if not g.is_input:
                bs.extend(
                    [integer_to_operator.index(g.operation)] + \
                    [circuit.gate.index(gi) for gi in g.inputs]
                )

        return record(bytes(bs))

    @staticmethod
    def from_base64(string: str) -> record:
        """
        Construct an instance from a Base64-encoded string representation of a record.

        >>> record.from_base64('CQACBAEDBgQ=').hex()
        '0900020401030604'
        """
        return record(base64.standard_b64decode(string))

    def to_circuit(self: record, truthtable: tuple) -> circuit.circuit:
        """
        Decode this record into a :obj:`~circuit.circuit.circuit` object.

        >>> c = record.from_base64('CQACBAEDBgQ=').to_circuit((0, 0, 1, 0, 0, 0, 0, 1))
        >>> c.gate.to_legible()
        (('id',), ('id',), ('id',), ('xor', 0, 2), ('nimp', 1, 3), ('id', 4))
        """
        # Create table for converting an encoded operator into an actual operator value.
        integer_to_operator = list(sorted(list(logical.every)))

        # Parse the gate information from the encoded representation.
        (j, ts) = (0, [])
        while j < len(self):
            operator = integer_to_operator[self[j]]
            ts.append((operator, self[j + 1: j + 1 + operator.arity()]))
            j += 1 + operator.arity()

        # Build the circuit object programmatically.
        arity = int(math.log2(len(truthtable)))
        coarity = len(truthtable[0]) if isinstance(truthtable[0], tuple) else 1
        c = circuit.circuit()
        gs = []
        for _ in range(arity): # Input gates.
            gs.append(c.gate(logical.id_, [], is_input=True))
        for entry in ts[0:-coarity]: # Internal gates.
            gs.append(c.gate(entry[0], [gs[k] for k in entry[1]]))
        for entry in ts[-coarity:]: # Output gates.
            c.gate(entry[0], [gs[k] for k in entry[1]], is_output=True)

        return c

    def to_base64(self: record) -> str:
        """
        Convert this instance into a Base64-encoded string representation.

        >>> c = circuit.circuit()
        >>> g0 = c.gate(logical.id_, is_input=True)
        >>> g1 = c.gate(logical.not_, [g0])
        >>> g2 = c.gate(logical.id_, [g1], is_output=True)
        >>> record.from_circuit(c).to_base64()
        'DAAGAQ=='
        """
        return base64.standard_b64encode(self).decode('utf-8')

class records(list):
    """
    Wrapper class for a base-level operation-to-circuit map (corresponding to a fixed
    combination of arity, coarity, operator set, and operator set to minimize).
    """
    def __getitem__(self: records, truthtable: tuple) -> record:
        """
        Data retrieval wrapper that performs normalization of the truth table,
        but does not check that it has a correct structure. To ensure the supplied
        truth table representation is valid, the :obj:`circuitdb.__call__` should
        be used to retrieve circuit data.
        """
        # Normalize the truth table representation (no validation) and
        # convert it into an index into the data.
        if all(isinstance(e, tuple) for e in truthtable):
            truthtable = tuple(tuple(map(int, e)) for e in truthtable)
            ls = set(len(e) for e in truthtable)
            if len(ls) == 1 and list(ls)[0] == 1:
                truthtable = list(e[0] for e in truthtable)
                index = int(bitlist.bitlist(truthtable))
            else:
                index = int(bitlist.bitlist([b for t in truthtable for b in t]))
        else:
            truthtable = list(map(int, truthtable))
            index = int(bitlist.bitlist(truthtable))

        # Retrieve, decode, and return the circuit data.
        return record(super().__getitem__(index)).to_circuit(truthtable)

# Set up containers for each (arity, coarity, operator set) combination
# for which data is included.
for i in range(0, 4):
    _db._data[i] = {}

    if i == 0:
        _db._data[i][1] = {
            frozenset(logical.every): {}
        }

    if i in range(1, 4):
        _db._data[i][1] = {
            frozenset([logical.id_, logical.not_, logical.and_, logical.or_]): {},
            frozenset([logical.id_, logical.not_, logical.and_, logical.xor_]): {},
            frozenset(logical.every): {}
        }

    if i == 2:
        _db._data[i][2] = {
            frozenset([logical.id_, logical.not_, logical.and_, logical.or_]): {},
            frozenset([logical.id_, logical.not_, logical.and_, logical.xor_]): {},
            frozenset(logical.every): {}
        }

_db._data\
    [1][1]\
    [frozenset([logical.id_, logical.not_, logical.and_, logical.or_])]\
    [frozenset([logical.id_, logical.not_, logical.and_, logical.or_])]\
    = records(map(base64.standard_b64decode, [
        'DAADAAEGAg==',
        'BgA=',
        'DAAGAQ==',
        'DAAKAAEGAg==',
    ]))

_db._data\
    [2][1]\
    [frozenset([logical.id_, logical.not_, logical.and_, logical.or_])]\
    [frozenset([logical.id_, logical.not_, logical.and_, logical.or_])]\
    = records(map(base64.standard_b64decode, [
        'DAADAAIGAw==',
        'AwABBgI=',
        'DAEDAAIGAw==',
        'BgA=',
        'DAADAQIGAw==',
        'BgE=',
        'AwABDAIKAAEDAwQGBQ==',
        'CgABBgI=',
        'CgABDAIGAw==',
        'AwABCgABDAMKAgQGBQ==',
        'DAEGAg==',
        'DAEKAAIGAw==',
        'DAAGAg==',
        'DAAKAQIGAw==',
        'AwABDAIGAw==',
        'DAAKAAIGAw==',
    ]))

_db._data\
    [2][2]\
    [frozenset([logical.id_, logical.not_, logical.and_, logical.or_])]\
    [frozenset([logical.id_, logical.not_, logical.and_, logical.or_])]\
    = records(map(base64.standard_b64decode, [
        'DAADAAIGAwYD',
        'DAADAAEDAAIGBAYD',
        'DAADAAEDAAIGAwYE',
        'AwABBgIGAg==',
        'DAEDAAIDAQIGBAYD',
        'DAADAAIGAwYA',
        'DAEDAAEDAAIGAwYE',
        'AwABBgIGAA==',
        'DAEDAAIDAQIGAwYE',
        'DAEDAAEDAAIGBAYD',
        'DAADAAIGAAYD',
        'AwABBgAGAg==',
        'DAEDAAIGAwYD',
        'DAEDAAIGAwYA',
        'DAEDAAIGAAYD',
        'BgAGAA==',
        'DAADAAIDAQIGAwYE',
        'DAADAAIGAwYB',
        'DAADAAEDAQIGAwYE',
        'AwABBgIGAQ==',
        'AwABDAIDAgMKAAEDAwUGBAYG',
        'DAADAAIKAAEGAwYE',
        'AwABDAIKAAEDAwQGAgYF',
        'AwABCgABBgIGAw==',
        'DAAMAQMAAwMBAgYEBgU=',
        'DAEDAAIGAwYB',
        'DAADAQIGAAYD',
        'BgAGAQ==',
        'DAAMAQMAAwMBAgoEBQYEBgY=',
        'DAEDAAIKAAEGAwYE',
        'AwABDAIKAAEDAwQGAAYF',
        'CgABBgAGAg==',
        'DAADAAIDAQIGBAYD',
        'DAADAAEDAQIGBAYD',
        'DAADAAIGAQYD',
        'AwABBgEGAg==',
        'DAAMAQMAAwMBAgYFBgQ=',
        'DAADAQIGAwYA',
        'DAEDAAIGAQYD',
        'BgEGAA==',
        'AwABDAIDAgMKAAEDAwUGBgYE',
        'AwABDAIKAAEDAwQGBQYC',
        'DAADAAIKAAEGBAYD',
        'AwABCgABBgMGAg==',
        'DAAMAQMAAwMBAgoEBQYGBgQ=',
        'AwABDAIKAAEDAwQGBQYA',
        'DAEDAAIKAAEGBAYD',
        'CgABBgIGAA==',
        'DAADAQIGAwYD',
        'DAADAQIGAwYB',
        'DAADAQIGAQYD',
        'BgEGAQ==',
        'DAAMAQMAAwMBAgoEBQYFBgY=',
        'DAADAQIKAAEGAwYE',
        'AwABDAIKAAEDAwQGAQYF',
        'CgABBgEGAg==',
        'DAAMAQMAAwMBAgoEBQYGBgU=',
        'AwABDAIKAAEDAwQGBQYB',
        'DAADAQIKAAEGBAYD',
        'CgABBgIGAQ==',
        'AwABDAIKAAEDAwQGBQYF',
        'AwABDAIKAAEDAwQGBQYE',
        'AwABDAIKAAEDAwQGBAYF',
        'CgABBgIGAg==',
        'CgABDAIDAAMGBAYD',
        'AwABCgABDAMDAAQKAgQGBQYG',
        'AwABCgABDAMGAgYE',
        'AwABCgABDAMKAgQGAgYF',
        'DAEDAQIGAwYC',
        'DAEDAQIKAAIGAwYE',
        'DAEDAAEGAwYC',
        'DAEDAAEKAAIGAwYE',
        'DAAMAQMAAwMCAwYEBgU=',
        'DAEDAAIMAwoAAgMEBQYDBgY=',
        'CgABDAIGAAYD',
        'AwABCgABDAMKAgQGAAYF',
        'DAEDAAIGAwYC',
        'DAEDAAIKAAIGAwYE',
        'DAEGAAYC',
        'DAEKAAIGAAYD',
        'DAADAAIGAwYC',
        'DAADAAIKAQIGAwYE',
        'DAADAAEGAwYC',
        'DAADAAEKAQIGAwYE',
        'AwABDAIDAgMGBAYD',
        'DAADAAIMAwYDBgQ=',
        'AwABDAIGAgYD',
        'DAADAAEKAAIGAwYE',
        'DAAMAQMAAwYEBgI=',
        'DAAKAQIMAwYEBgM=',
        'DAAGAAYC',
        'DAAKAQIGAAYD',
        'AwABDAIDAAMGBAYD',
        'DAEDAAIKAQIGAwYE',
        'AwABDAIGAAYD',
        'DAAKAAIGAAYD',
        'DAAMAQMBAgMCAwYEBgU=',
        'DAADAQIMAwoBAgMEBQYDBgY=',
        'CgABDAIGAQYD',
        'AwABCgABDAMKAgQGAQYF',
        'DAAMAQMBAgYEBgM=',
        'DAADAQIMAwYDBgQ=',
        'DAEGAQYC',
        'DAEKAAIGAQYD',
        'AwABDAIKAAEMBAMDBAYGBgU=',
        'AwABDAIKAAEDAwQMBQYFBgY=',
        'CgABDAIGAgYD',
        'AwABCgABDAMKAgQGAwYF',
        'DAAMAQMAAwMBAgoEBQYGBgM=',
        'DAEDAAIKAAIMBAoDBQYGBgQ=',
        'DAEKAAEGAwYC',
        'DAEKAAEKAAIGAwYE',
        'DAADAQIGAwYC',
        'DAADAQIKAQIGAwYE',
        'DAAGAQYC',
        'DAAKAQIGAQYD',
        'AwABDAIDAQMGBAYD',
        'DAADAQIKAAIGAwYE',
        'AwABDAIGAQYD',
        'DAAKAAIGAQYD',
        'DAAMAQMAAwMBAgoEBQYGBgI=',
        'DAADAQIKAQIMBAoDBQYGBgQ=',
        'DAAKAAEGAwYC',
        'DAAKAAEKAQIGAwYE',
        'AwABDAIKAAEDAwQGBQYD',
        'AwABDAIKAAEDAwQKAAMGBQYG',
        'AwABDAIKAAEGBAYD',
        'DAAKAAEKAAIGAwYE',
        'CgABDAIDAAMGAwYE',
        'AwABCgABDAMGBAYC',
        'AwABCgABDAMDAAQKAgQGBgYF',
        'AwABCgABDAMKAgQGBQYC',
        'DAAMAQMAAwMCAwYFBgQ=',
        'CgABDAIGAwYA',
        'DAEDAAIMAwoAAgMEBQYGBgM=',
        'AwABCgABDAMKAgQGBQYA',
        'DAEDAQIGAgYD',
        'DAEDAAEGAgYD',
        'DAEDAQIKAAIGBAYD',
        'DAEDAAEKAAIGBAYD',
        'DAEDAAIGAgYD',
        'DAEGAgYA',
        'DAEDAAIKAAIGBAYD',
        'DAEKAAIGAwYA',
        'DAAMAQMBAgMCAwYFBgQ=',
        'CgABDAIGAwYB',
        'DAADAQIMAwoBAgMEBQYGBgM=',
        'AwABCgABDAMKAgQGBQYB',
        'AwABDAIKAAEMBAMDBAYFBgY=',
        'CgABDAIGAwYC',
        'AwABDAIKAAEDAwQMBQYGBgU=',
        'AwABCgABDAMKAgQGBQYD',
        'DAAMAQMBAgYDBgQ=',
        'DAEGAgYB',
        'DAADAQIMAwYEBgM=',
        'DAEKAAIGAwYB',
        'DAAMAQMAAwMBAgoEBQYDBgY=',
        'DAEKAAEGAgYD',
        'DAEDAAIKAAIMBAoDBQYEBgY=',
        'DAEKAAEKAAIGBAYD',
        'DAADAAIGAgYD',
        'DAADAAEGAgYD',
        'DAADAAIKAQIGBAYD',
        'DAADAAEKAQIGBAYD',
        'DAAMAQMAAwYCBgQ=',
        'DAAGAgYA',
        'DAAKAQIMAwYDBgQ=',
        'DAAKAQIGAwYA',
        'AwABDAIDAgMGAwYE',
        'AwABDAIGAwYC',
        'DAADAAIMAwYEBgM=',
        'DAADAAEKAAIGBAYD',
        'AwABDAIDAAMGAwYE',
        'AwABDAIGAwYA',
        'DAEDAAIKAQIGBAYD',
        'DAAKAAIGAwYA',
        'DAADAQIGAgYD',
        'DAAGAgYB',
        'DAADAQIKAQIGBAYD',
        'DAAKAQIGAwYB',
        'DAAMAQMAAwMBAgoEBQYCBgY=',
        'DAAKAAEGAgYD',
        'DAADAQIKAQIMBAoDBQYEBgY=',
        'DAAKAAEKAQIGBAYD',
        'AwABDAIDAQMGAwYE',
        'AwABDAIGAwYB',
        'DAADAQIKAAIGBAYD',
        'DAAKAAIGAwYB',
        'AwABDAIKAAEDAwQGAwYF',
        'AwABDAIKAAEGAwYE',
        'AwABDAIKAAEDAwQKAAMGBgYF',
        'DAAKAAEKAAIGBAYD',
        'CgABDAIGAwYD',
        'AwABCgABDAMKAgQGBAYF',
        'AwABCgABDAMKAgQGBQYE',
        'AwABCgABDAMKAgQGBQYF',
        'DAAMAQMCAwYEBgM=',
        'CgABDAIKAAMGAwYE',
        'DAAMAQMAAQMCAwoEBQYGBgM=',
        'DAAMAQoAAwoBAgMEBQYGBgQ=',
        'DAAMAQMCAwYDBgQ=',
        'DAAMAQMAAQMCAwoEBQYDBgY=',
        'CgABDAIKAAMGBAYD',
        'DAAMAQoAAwoBAgMEBQYEBgY=',
        'DAEGAgYC',
        'DAEKAAIGAgYD',
        'DAEKAAIGAwYC',
        'DAEKAAIGAwYD',
        'DAAMAQMCAwYEBgI=',
        'CgABDAIKAQMGAwYE',
        'DAAMAQMAAQMCAwoEBQYGBgI=',
        'DAAMAQoAAwoBAgMEBQYGBgU=',
        'DAAMAQMCAwoCAwYEBgU=',
        'CgABDAIKAgMGAwYE',
        'AwABDAIKAAEMBAoCBQYGBgM=',
        'AwABCgABDAMKAgQKAwQGBQYG',
        'DAAMAQYDBgI=',
        'DAAMAQoBAgYDBgQ=',
        'DAAMAQoAAwYEBgI=',
        'DAAMAQoAAwoBAgYEBgU=',
        'DAAMAQoCAwYDBgQ=',
        'DAEKAQIGAgYD',
        'DAAMAQoAAwoCAwYEBgU=',
        'DAEKAAIKAQIGAwYE',
        'DAAMAQMCAwYCBgQ=',
        'DAAMAQMAAQMCAwoEBQYCBgY=',
        'CgABDAIKAQMGBAYD',
        'DAAMAQoAAwoBAgMEBQYFBgY=',
        'DAAMAQYCBgM=',
        'DAAMAQoAAwYCBgQ=',
        'DAAMAQoBAgYEBgM=',
        'DAAMAQoAAwoBAgYFBgQ=',
        'DAAMAQMCAwoCAwYFBgQ=',
        'AwABDAIKAAEMBAoCBQYDBgY=',
        'CgABDAIKAgMGBAYD',
        'AwABCgABDAMKAgQKAwQGBgYF',
        'DAAMAQoCAwYEBgM=',
        'DAAMAQoAAwoCAwYFBgQ=',
        'DAEKAQIGAwYC',
        'DAEKAAIKAQIGBAYD',
        'DAAGAgYC',
        'DAAKAQIGAgYD',
        'DAAKAQIGAwYC',
        'DAAKAQIGAwYD',
        'DAAMAQoCAwYCBgQ=',
        'DAAKAAIGAgYD',
        'DAAMAQoBAgoCAwYEBgU=',
        'DAAKAAIKAQIGBAYD',
        'DAAMAQoCAwYEBgI=',
        'DAAMAQoBAgoCAwYFBgQ=',
        'DAAKAAIGAwYC',
        'DAAKAAIKAQIGAwYE',
        'AwABDAIGAwYD',
        'AwABDAIKAAMGAwYE',
        'AwABDAIKAAMGBAYD',
        'DAAKAAIGAwYD',
    ]))

_db._data\
    [3][1]\
    [frozenset([logical.id_, logical.not_, logical.and_, logical.or_])]\
    [frozenset([logical.id_, logical.not_, logical.and_, logical.or_])]\
    = records(map(base64.standard_b64decode, [
        'DAADAAMGBA==',
        'AwABAwIDBgQ=',
        'DAIDAAEDAwQGBQ==',
        'AwABBgM=',
        'DAEDAAIDAwQGBQ==',
        'AwACBgM=',
        'AwECDAMDAAQKAQIDBQYGBw==',
        'CgECAwADBgQ=',
        'CgECDAMDAAQGBQ==',
        'AwECCgECDAQKAwUDAAYGBw==',
        'DAIDAAMGBA==',
        'DAIKAQMDAAQGBQ==',
        'DAEDAAMGBA==',
        'DAEKAgMDAAQGBQ==',
        'AwECDAMDAAQGBQ==',
        'BgA=',
        'DAADAQIDAwQGBQ==',
        'AwECBgM=',
        'AwACDAMDAQQKAAIDBQYGBw==',
        'CgACAwEDBgQ=',
        'AwABDAMDAgQKAAEDBQYGBw==',
        'CgABAwIDBgQ=',
        'AwABAwIDDAQKAAEDAgYKAwcDBQgGCQ==',
        'AwABCgABAwIECgMFBgY=',
        'AwECCgADCgECAwAFDAYDBAcGCA==',
        'AwECCgECDAQDAAUKAwYGBw==',
        'AwACDAMDAQIKAAUDBAYGBw==',
        'DAIDAAMDAQIKBAUGBg==',
        'AwABDAMDAQIKAAUDBAYGBw==',
        'DAEDAAMDAQIKBAUGBg==',
        'AwECAwADDAQKAAMDBQYGBw==',
        'AwECCgADBgQ=',
        'CgACDAMDAQQGBQ==',
        'AwACCgACDAQKAwUDAQYGBw==',
        'DAIDAQMGBA==',
        'DAIKAAMDAQQGBQ==',
        'AwACCgACAwEEDAUKAQMDBgcGCA==',
        'AwACCgACDAQDAQUKAwYGBw==',
        'AwACAwECDAQKAQMDBQYGBw==',
        'DAIDAAIDAQMKBAUGBg==',
        'AwABCgABCgIDDAUDBAYGBw==',
        'AwABAwIDCgABCgIDDAYDBQcKBAgGCQ==',
        'DAIKAAEDAwQGBQ==',
        'DAIDAAEKAAEDAwUKBAYGBw==',
        'CgABCgACAwEEDAUDAwYGBw==',
        'DAEKAgMDAAQKAAQMBgoFBwYI',
        'AwECDAMKAAEDBAUGBg==',
        'DAIDAQMKAAQGBQ==',
        'DAADAQMGBA==',
        'DAAKAgMDAQQGBQ==',
        'AwACDAMDAQQGBQ==',
        'BgE=',
        'AwABDAMDAAIKAQUDBAYGBw==',
        'DAADAAIDAQMKBAUGBg==',
        'AwACAwEDDAQKAQMDBQYGBw==',
        'AwACCgEDBgQ=',
        'CgABCgECAwAEDAUDAwYGBw==',
        'DAAKAgMDAQQKAQQMBgoFBwYI',
        'AwACDAMKAAEDBAUGBg==',
        'DAIDAAMKAQQGBQ==',
        'AwABDAMKAAEDBAUGBg==',
        'AwABDAMKAAEKAgQDBQYGBw==',
        'AwABAwIDDAQKAAEDBQYGBw==',
        'CgABBgM=',
        'CgABDAMDAgQGBQ==',
        'AwABCgABDAQKAwUDAgYGBw==',
        'AwABCgABAwIEDAUKAgMDBgcGCA==',
        'AwABCgABDAQDAgUKAwYGBw==',
        'DAEDAgMGBA==',
        'DAEKAAMDAgQGBQ==',
        'AwABAwECDAQKAgMDBQYGBw==',
        'DAEDAAEDAgMKBAUGBg==',
        'AwACCgACCgEDDAUDBAYGBw==',
        'AwACAwEDCgACCgEDDAYDBQcKBAgGCQ==',
        'CgABAwIDDAQKAAIDBQYGBw==',
        'DAEDAgMDAAQMBQoABAMGBwYI',
        'DAEKAAIDAwQGBQ==',
        'DAEDAAIKAAIDAwUKBAYGBw==',
        'AwECDAMKAAIDBAUGBg==',
        'DAEDAgMKAAQGBQ==',
        'DAADAgMGBA==',
        'DAAKAQMDAgQGBQ==',
        'AwABAwACDAQKAgMDBQYGBw==',
        'DAADAAEDAgMKBAUGBg==',
        'AwABDAMDAgQGBQ==',
        'BgI=',
        'AwABAwIDDAQKAgMDBQYGBw==',
        'AwABCgIDBgQ=',
        'CgACCgECAwAEDAUDAwYGBw==',
        'DAAKAQMDAgQKAgQMBgoFBwYI',
        'AwACDAMKAAIDBAUGBg==',
        'AwACDAMKAAIKAQQDBQYGBw==',
        'AwABDAMKAAIDBAUGBg==',
        'DAEDAAMKAgQGBQ==',
        'AwABAwIDDAQKAAIDBQYGBw==',
        'CgACBgM=',
        'AwECCgADDAQKAQIDBQYGBw==',
        'AwECAwADCgADDAUKAQIDBgcKBAgGCQ==',
        'CgABAwIDDAQKAQIDBQYGBw==',
        'DAADAgMDAQQMBQoBBAMGBwYI',
        'CgACAwEDDAQKAQIDBQYGBw==',
        'DAADAQMDAgQMBQoCBAMGBwYI',
        'AwECDAMKAQIDBAUGBg==',
        'AwECDAMKAAQKAQIDBQYGBw==',
        'AwABCgABAwIECgIECgMFDAcDBggGCQ==',
        'AwABDAMKAAEDBAUDAgYMBwoCBgMICQYK',
        'CgABAwIDDAQKAgMDBQYGBw==',
        'AwABCgABAwIEDAUKAgQDBgcKAwgGCQ==',
        'CgACAwEDDAQKAQMDBQYGBw==',
        'AwACCgACAwEEDAUKAQQDBgcKAwgGCQ==',
        'AwECDAMKAAEKAgUDBAYGBw==',
        'AwECDAMKAQIDBAUKAAYGBw==',
        'DAAKAQIDAwQGBQ==',
        'DAADAQIKAQIDAwUKBAYGBw==',
        'AwACDAMKAQIDBAUGBg==',
        'DAADAgMKAQQGBQ==',
        'AwABDAMKAQIDBAUGBg==',
        'DAADAQMKAgQGBQ==',
        'AwABAwIDDAQKAQIDBQYGBw==',
        'CgECBgM=',
        'CgECAwADDAQKAAMDBQYGBw==',
        'AwECCgECAwAEDAUKAAQDBgcKAwgGCQ==',
        'AwACDAMKAAEKAgUDBAYGBw==',
        'AwACDAMKAAIDBAUKAQYGBw==',
        'AwABDAMKAAEKAgUDBAYGBw==',
        'AwABDAMKAAEDBAUKAgYGBw==',
        'AwABAwIDDAQKAAEKAgYDBQcGCA==',
        'CgABCgIDBgQ=',
        'CgABCgIDDAQGBQ==',
        'AwABAwIDCgABCgIFDAYKBAcGCA==',
        'DAADAQMKAQMKAgQMBgMFBwYI',
        'AwABCgABCgIEDAUKAwYGBw==',
        'DAADAgMKAQQMBQoCAwMGBwYI',
        'AwACCgABCgIEDAUKAwYGBw==',
        'AwECCgECAwAEDAUKAAQDBgcKAwgMCQYK',
        'CgECAwADCgADDAUKBAYGBw==',
        'CgECDAMGBA==',
        'AwABAwIDCgECDAUKBAYGBw==',
        'DAADAQMKAgQMBQYG',
        'AwABCgECDAQKAwUGBg==',
        'DAADAgMKAQQMBQYG',
        'AwACCgECDAQKAwUGBg==',
        'DAADAQIKAQIDAwUKBAYMBwYI',
        'CgECDAMKAAQGBQ==',
        'DAADAQIKAQIMBQoEBgMDBwYI',
        'AwECCgABCgIEDAUKAwYGBw==',
        'AwACCgACAwEEDAUKAQQDBgcKAwgMCQYK',
        'CgACAwEDCgEDDAUKBAYGBw==',
        'AwABCgABAwIEDAUKAgQDBgcKAwgMCQYK',
        'CgABAwIDCgIDDAUKBAYGBw==',
        'AwECCgECDAQKAwUDAAYMBwoABgMICQYK',
        'AwABCgABAwIECgIEDAYKAwUKBwgGCQ==',
        'DAADAQIDAwQKAQIMBgoFBwYI',
        'AwECCgECDAQKAwUGBg==',
        'DAADAQMDAgQKAgQMBgoFBwYI',
        'CgACAwEDCgECDAUKBAYGBw==',
        'DAADAgMDAQQKAQQMBgoFBwYI',
        'CgABAwIDCgECDAUKBAYGBw==',
        'AwECAwADCgADDAUKAQIDBgcKBAgMCQYK',
        'AwECCgADCgECDAUKBAYGBw==',
        'CgACDAMGBA==',
        'AwABAwIDCgACDAUKBAYGBw==',
        'DAAMAgoBAwMEBQYG',
        'AwABCgACDAQKAwUGBg==',
        'DAAKAQMDAgQMBQoCAwMGBwYI',
        'AwACCgACDAQKAwUGBg==',
        'DAAKAQMDAgQMBQoCBAMGBwYI',
        'CgACDAMKAQIDAAUKBAYGBw==',
        'AwABCgIDDAQGBQ==',
        'AwABAwIDCgIDDAUKBAYGBw==',
        'DAIGAw==',
        'DAIDAAEKAwQGBQ==',
        'DAADAAEDAgMKBAUMBgYH',
        'AwABAwACCgIDDAUKBAYGBw==',
        'DAAKAQMDAgQMBQYG',
        'DAIKAAMGBA==',
        'DAAMAgoBBAMDBQYG',
        'AwECCgACDAQKAwUGBg==',
        'DAAMAgMBAwoBAwMEBgoFBwYI',
        'CgACDAMKAQQGBQ==',
        'DAEDAgMDAAQKAAQMBgoFBwYI',
        'CgABAwIDCgACDAUKBAYGBw==',
        'AwACAwEDCgACCgEDDAYDBQcKBAgMCQYK',
        'AwACCgACDAQKAQMKBQYGBw==',
        'DAADAQMKAQIMBQoEBgYH',
        'AwABAwECCgIDDAUKBAYGBw==',
        'DAAMAgMBAwoEBQYG',
        'DAIKAQMGBA==',
        'DAADAQMDAgMKAQUMBgoEBwYI',
        'AwABCgABAwIECgIDDAYKBQcGCA==',
        'DAADAQMKAQMDAgUMBgoEBwYI',
        'DAIKAAEKAwQGBQ==',
        'CgABDAMGBA==',
        'AwABAwIDCgABDAUKBAYGBw==',
        'DAAKAQMKAgMDAQUMBgMEBwYI',
        'AwABCgABDAQKAwUGBg==',
        'DAAMAQoCAwMEBQYG',
        'AwACCgABDAQKAwUGBg==',
        'DAAKAgMDAQQMBQoBBAMGBwYI',
        'CgABDAMKAQIDAAUKBAYGBw==',
        'AwACCgEDDAQGBQ==',
        'AwACAwEDCgEDDAUKBAYGBw==',
        'DAADAAIDAQMKBAUMBgYH',
        'AwABAwACCgEEDAUKAwYGBw==',
        'DAEGAw==',
        'DAEDAAIKAwQGBQ==',
        'DAAKAgMDAQQMBQYG',
        'DAEKAAMGBA==',
        'DAAMAQoCBAMDBQYG',
        'AwECCgABDAQKAwUGBg==',
        'DAEKAgMDAAQMBQoABAMGBwYI',
        'CgABDAMKAAIDAQUKBAYGBw==',
        'DAAMAQMCAwoCAwMEBgoFBwYI',
        'CgABDAMKAgQGBQ==',
        'AwABAwIDCgABCgIDDAYDBQcKBAgMCQYK',
        'AwABCgABDAQKAgMKBQYGBw==',
        'DAADAgMKAQIMBQoEBgYH',
        'AwACAwECCgEDDAUKBAYGBw==',
        'DAADAQMDAgMKAgQMBgoFBwYI',
        'AwACCgACAwEECgEDDAYKBQcGCA==',
        'DAAMAQMCAwoEBQYG',
        'DAEKAgMGBA==',
        'DAADAgMKAgMDAQUMBgoEBwYI',
        'DAEKAAIKAwQGBQ==',
        'AwECCgADDAQGBQ==',
        'AwECAwADCgADDAUKBAYGBw==',
        'DAADAQIMBAoBAwMFBgYH',
        'AwABAwECCgAEDAUKAwYGBw==',
        'DAADAQIMBAoCAwMFBgYH',
        'AwACAwECCgAEDAUKAwYGBw==',
        'DAADAQIMBAoBAgoDBgMFBwYI',
        'AwECCgADDAQKAQIDAAYKBQcGCA==',
        'AwABCgABAwIECgMFDAYGBw==',
        'AwABAwIDCgABAwIFCgMGDAcKBAgGCQ==',
        'CgABAwIDDAQGBQ==',
        'AwABCgABAwIEDAUKAwYGBw==',
        'CgACAwEDDAQGBQ==',
        'AwACCgACAwEEDAUKAwYGBw==',
        'AwECDAMGBA==',
        'AwECDAMKAAQGBQ==',
        'DAAGAw==',
        'DAADAQIKAwQGBQ==',
        'DAAMAgMBBAoDBQYG',
        'DAAKAQMGBA==',
        'DAAMAQMCBAoDBQYG',
        'DAAKAgMGBA==',
        'DAADAQIMBAoBAgMFBgoDBwYI',
        'DAAKAQIKAwQGBQ==',
        'CgECAwADDAQGBQ==',
        'AwECCgECAwAEDAUKAwYGBw==',
        'AwACDAMGBA==',
        'AwACDAMKAQQGBQ==',
        'AwABDAMGBA==',
        'AwABDAMKAgQGBQ==',
        'AwABAwIDDAQGBQ==',
        'DAAKAAMGBA==',
    ]))

_db._data\
    [1][1]\
    [frozenset([logical.id_, logical.not_, logical.and_, logical.xor_])]\
    [frozenset([logical.and_])]\
    = records(map(base64.standard_b64decode, [
        'DAAMAAkBAgYD',
        'BgA=',
        'DAAGAQ==',
        'DAAJAAEGAg==',
    ]))

_db._data\
    [2][1]\
    [frozenset([logical.id_, logical.not_, logical.and_, logical.xor_])]\
    [frozenset([logical.and_])]\
    = records(map(base64.standard_b64decode, [
        'DAAMAAkCAwYE',
        'AwABBgI=',
        'DAEDAAIGAw==',
        'BgA=',
        'DAADAQIGAw==',
        'BgE=',
        'CQABBgI=',
        'DAADAQIJAAMGBA==',
        'DAAMAQMCAwYE',
        'DAAJAQIGAw==',
        'DAEGAg==',
        'DAADAQIMAwYE',
        'DAAGAg==',
        'DAADAAEJAgMGBA==',
        'AwABDAIGAw==',
        'DAAJAAIGAw==',
    ]))

_db._data\
    [2][2]\
    [frozenset([logical.id_, logical.not_, logical.and_, logical.xor_])]\
    [frozenset([logical.and_])]\
    = records(map(base64.standard_b64decode, [
        'DAADAAIGAwYD',
        'DAADAAEDAAIGBAYD',
        'DAADAAEDAAIGAwYE',
        'AwABBgIGAg==',
        'DAEDAAIDAQIGBAYD',
        'DAADAAIGAwYA',
        'AwABCQACBgIGAw==',
        'AwABBgIGAA==',
        'DAEDAAIDAQIGAwYE',
        'AwABCQACBgMGAg==',
        'DAADAAIGAAYD',
        'AwABBgAGAg==',
        'DAEDAAIGAwYD',
        'DAEDAAIGAwYA',
        'DAEDAAIGAAYD',
        'BgAGAAYA',
        'DAADAAIDAQIGAwYE',
        'DAADAAIGAwYB',
        'AwABCQECBgIGAw==',
        'AwABBgIGAQ==',
        'DAADAAIJAAEGAwYE',
        'DAADAAIDAQIJAAQGAwYF',
        'AwABCQABBgIGAw==',
        'AwABCQABCQIDBgIGBA==',
        'AwABCQACCQECBgMGBA==',
        'DAEDAAIGAwYB',
        'DAADAQIGAAYD',
        'BgAGAAYB',
        'CQABAwACBgMGAg==',
        'DAEDAAIJAQMGAwYE',
        'CQABBgAGAg==',
        'DAADAQIJAAMGAAYE',
        'DAADAAIDAQIGBAYD',
        'AwABCQECBgMGAg==',
        'DAADAAIGAQYD',
        'AwABBgEGAg==',
        'AwABCQACCQECBgQGAw==',
        'DAADAQIGAwYA',
        'DAEDAAIGAQYD',
        'BgAGAQYA',
        'DAADAAIJAAEGBAYD',
        'AwABCQABBgMGAg==',
        'DAADAAIDAQIJAAQGBQYD',
        'AwABCQABCQIDBgQGAg==',
        'CQABAwACBgIGAw==',
        'CQABBgIGAA==',
        'DAEDAAIJAQMGBAYD',
        'DAADAQIJAAMGBAYA',
        'DAADAQIGAwYD',
        'DAADAQIGAwYB',
        'DAADAQIGAQYD',
        'BgAGAQYB',
        'CQABAwECBgMGAg==',
        'DAADAQIJAAMGAwYE',
        'CQABBgEGAg==',
        'DAADAQIJAAMGAQYE',
        'CQABAwECBgIGAw==',
        'CQABBgIGAQ==',
        'DAADAQIJAAMGBAYD',
        'DAADAQIJAAMGBAYB',
        'CQABBgIGAg==',
        'AwABCQABCQIDBgMGBA==',
        'AwABCQABCQIDBgQGAw==',
        'DAADAQIJAAMGBAYE',
        'DAAMAQMAAgMCAwYEBgU=',
        'DAADAAIJAQIGAwYE',
        'DAAMAQMAAQMCAwYEBgU=',
        'DAADAAEJAQIGAwYE',
        'DAEDAQIGAwYC',
        'DAADAAIDAQIMBAYDBgU=',
        'DAEDAAEGAwYC',
        'DAEDAAEJAgMGAwYE',
        'DAEDAAIJAgMGAwYE',
        'DAEDAAIJAAIGAwYE',
        'DAAMAQMCAwYABgQ=',
        'DAAJAQIGAAYD',
        'DAEDAAIGAwYC',
        'DAEDAAEDAAIJAgMGBAYF',
        'DAEGAAYC',
        'DAADAQIMAwYABgQ=',
        'DAADAAIGAwYC',
        'DAADAAEDAAIJAgMGBAYF',
        'DAADAAEGAwYC',
        'DAADAAEJAgMGAwYE',
        'AwABDAIDAgMGBAYD',
        'DAADAAIMAwYDBgQ=',
        'AwABDAIGAgYD',
        'DAADAAEJAAIGAwYE',
        'DAAMAQMAAwYEBgI=',
        'DAEDAAIMAwYDBgQ=',
        'DAAGAAYC',
        'DAADAAEJAgMGAAYE',
        'AwABDAIDAAMGBAYD',
        'DAEDAAIJAQIGAwYE',
        'AwABDAIGAAYD',
        'DAAJAAIGAAYD',
        'DAADAQIJAgMGAwYE',
        'DAADAQIJAQIGAwYE',
        'DAAMAQMCAwYBBgQ=',
        'DAAJAQIGAQYD',
        'DAAMAQMBAgYEBgM=',
        'DAADAQIMAwYDBgQ=',
        'DAEGAQYC',
        'DAADAQIMAwYBBgQ=',
        'DAAMAQMCAwkAAQYFBgQ=',
        'CQABDAIGAgYD',
        'DAAMAQMCAwwEBgUGBA==',
        'DAADAQIJAAMJAQIGBAYF',
        'DAEJAAEGAwYC',
        'CQABAwECDAMGAgYE',
        'DAEDAAIJAQMGBAYC',
        'DAADAQIMAwkAAwYFBgQ=',
        'DAADAQIGAwYC',
        'DAADAAEDAQIJAgMGBAYF',
        'DAAGAQYC',
        'DAADAAEJAgMGAQYE',
        'AwABDAIDAQMGBAYD',
        'DAADAQIJAAIGAwYE',
        'AwABDAIGAQYD',
        'DAAJAAIGAQYD',
        'DAAJAAEGAwYC',
        'CQABAwACDAMGAgYE',
        'DAADAQIJAAMGBAYC',
        'DAEDAAIMAwkBAwYFBgQ=',
        'AwABDAIJAAEGBAYD',
        'DAAJAAEJAAIGAwYE',
        'AwABDAIDAAMJAQQGBQYD',
        'DAADAQIJAAIJAAMGBQYE',
        'DAAMAQMAAgMCAwYFBgQ=',
        'DAAMAQMAAQMCAwYFBgQ=',
        'DAADAAIJAQIGBAYD',
        'DAADAAEJAQIGBAYD',
        'DAEDAAIJAgMGBAYD',
        'DAAMAQMCAwYEBgA=',
        'DAEDAAIJAAIGBAYD',
        'DAAJAQIGAwYA',
        'DAEDAQIGAgYD',
        'DAEDAAEGAgYD',
        'DAADAAIDAQIMBAYFBgM=',
        'DAEDAAEJAgMGBAYD',
        'DAEDAAIGAgYD',
        'DAEGAgYA',
        'DAEDAAEDAAIJAgMGBQYE',
        'DAADAQIMAwYEBgA=',
        'DAADAQIJAgMGBAYD',
        'DAAMAQMCAwYEBgE=',
        'DAADAQIJAQIGBAYD',
        'DAAJAQIGAwYB',
        'DAAMAQMCAwkAAQYEBgU=',
        'DAAMAQMCAwwEBgQGBQ==',
        'CQABDAIGAwYC',
        'DAADAQIJAAMJAQIGBQYE',
        'DAAMAQMBAgYDBgQ=',
        'DAEGAgYB',
        'DAADAQIMAwYEBgM=',
        'DAADAQIMAwYEBgE=',
        'DAEJAAEGAgYD',
        'DAEDAAIJAQMGAgYE',
        'CQABAwECDAMGBAYC',
        'DAADAQIMAwkAAwYEBgU=',
        'DAADAAIGAgYD',
        'DAADAAEGAgYD',
        'DAADAAEDAAIJAgMGBQYE',
        'DAADAAEJAgMGBAYD',
        'DAAMAQMAAwYCBgQ=',
        'DAAGAgYA',
        'DAEDAAIMAwYEBgM=',
        'DAADAAEJAgMGBAYA',
        'AwABDAIDAgMGAwYE',
        'AwABDAIGAwYC',
        'DAADAAIMAwYEBgM=',
        'DAADAAEJAAIGBAYD',
        'AwABDAIDAAMGAwYE',
        'AwABDAIGAwYA',
        'DAEDAAIJAQIGBAYD',
        'DAAJAAIGAwYA',
        'DAADAQIGAgYD',
        'DAAGAgYB',
        'DAADAAEDAQIJAgMGBQYE',
        'DAADAAEJAgMGBAYB',
        'DAAJAAEGAgYD',
        'DAADAQIJAAMGAgYE',
        'CQABAwACDAMGBAYC',
        'DAEDAAIMAwkBAwYEBgU=',
        'AwABDAIDAQMGAwYE',
        'AwABDAIGAwYB',
        'DAADAQIJAAIGBAYD',
        'DAAJAAIGAwYB',
        'AwABDAIJAAEGAwYE',
        'AwABDAIDAAMJAQQGAwYF',
        'DAAJAAEJAAIGBAYD',
        'DAADAQIJAAIJAAMGBAYF',
        'DAAMAQMCAwYEBgQ=',
        'DAAJAQIDAgMGBAYD',
        'DAAJAQIDAgMGAwYE',
        'DAAJAQIGAwYD',
        'DAAMAQMCAwYEBgM=',
        'DAAMAQMCAwkABAYEBgU=',
        'DAEJAAIGAwYC',
        'DAADAQIMAwkBAgYFBgQ=',
        'DAAMAQMCAwYDBgQ=',
        'DAEJAAIGAgYD',
        'DAAMAQMCAwkABAYFBgQ=',
        'DAADAQIMAwkBAgYEBgU=',
        'DAEGAgYC',
        'DAEDAAEJAgMGAgYE',
        'DAEDAAEJAgMGBAYC',
        'DAADAQIMAwYEBgQ=',
        'DAAMAQMCAwYEBgI=',
        'DAAMAQMCAwkBBAYEBgU=',
        'DAAJAQIGAwYC',
        'DAADAAEJAQIJAgMGBAYF',
        'AwABDAIJAAEJAwQGBQYD',
        'DAAMAQMCAwkAAgYEBgU=',
        'DAADAAEMAwkBAgYFBgQ=',
        'DAAJAAIJAQIGBAYD',
        'DAAMAQYDBgI=',
        'DAEDAAIMAwYCBgQ=',
        'DAADAQIMAwYEBgI=',
        'AwABDAIJAAMJAQMGBQYE',
        'DAEDAAEMAwYCBgQ=',
        'DAEJAQIGAgYD',
        'AwABDAIJAQMGBAYD',
        'DAADAQIMAwkAAgYEBgU=',
        'DAAMAQMCAwYCBgQ=',
        'DAAJAQIGAgYD',
        'DAAMAQMCAwkBBAYFBgQ=',
        'DAADAAEJAQIJAgMGBQYE',
        'DAAMAQYCBgM=',
        'DAADAQIMAwYCBgQ=',
        'DAEDAAIMAwYEBgI=',
        'AwABDAIJAAMJAQMGBAYF',
        'AwABDAIJAAEJAwQGAwYF',
        'DAADAAEMAwkBAgYEBgU=',
        'DAAMAQMCAwkAAgYFBgQ=',
        'DAAJAAIJAQIGAwYE',
        'DAEDAAEMAwYEBgI=',
        'AwABDAIJAQMGAwYE',
        'DAEJAQIGAwYC',
        'DAADAQIMAwkAAgYFBgQ=',
        'DAAGAgYC',
        'DAADAAEJAgMGAgYE',
        'DAADAAEJAgMGBAYC',
        'DAADAAEJAgMGBAYE',
        'DAADAAEMAwYCBgQ=',
        'DAAJAAIGAgYD',
        'AwABDAIJAAMGBAYD',
        'DAADAAEJAAIJAgMGBQYE',
        'DAADAAEMAwYEBgI=',
        'AwABDAIJAAMGAwYE',
        'DAAJAAIGAwYC',
        'DAADAAEJAAIJAgMGBAYF',
        'AwABDAIGAwYD',
        'AwABDAIJAgMGAwYE',
        'AwABDAIJAgMGBAYD',
        'DAAJAAIGAwYD',
    ]))

_db._data\
    [3][1]\
    [frozenset([logical.id_, logical.not_, logical.and_, logical.xor_])]\
    [frozenset([logical.and_])]\
    = records(map(base64.standard_b64decode, [
        'DAAMAAkDBAYF',
        'AwABAwIDBgQ=',
        'DAIDAAEDAwQGBQ==',
        'AwABBgM=',
        'DAEDAAIDAwQGBQ==',
        'AwACBgM=',
        'CQECAwADBgQ=',
        'DAEDAgMJAQQDAAUGBg==',
        'DAEMAgMAAwMEBQYG',
        'DAEJAgMDAAQGBQ==',
        'DAIDAAMGBA==',
        'DAEDAAIDAwQJAAUGBg==',
        'DAEDAAMGBA==',
        'DAEDAQIJAwQDAAUGBg==',
        'AwABAwIDCQAEBgU=',
        'BgA=',
        'DAADAQIDAwQGBQ==',
        'AwECBgM=',
        'CQACAwEDBgQ=',
        'DAADAgMJAAQDAQUGBg==',
        'CQABAwIDBgQ=',
        'DAADAQMJAAQDAgUGBg==',
        'AwABCQABCQIDCQMEAwUGBgc=',
        'CQABCQACAwMECQAFBgY=',
        'CQABCQACAwMEBgU=',
        'DAEDAAMJAQQDAgUJBAYGBw==',
        'AwECCQACCQADAwQFBgY=',
        'CQABAwIDCQAEBgU=',
        'AwECCQABCQADAwQFBgY=',
        'CQACAwEDCQAEBgU=',
        'AwECCQADBgQ=',
        'DAADAQIDAwQJAAUGBg==',
        'DAAMAgMBAwMEBQYG',
        'DAAJAgMDAQQGBQ==',
        'DAIDAQMGBA==',
        'DAADAQIDAwQJAQUGBg==',
        'CQABCQECAwMEBgU=',
        'DAADAQMJAAQDAgUJBAYGBw==',
        'AwACCQECCQEDAwQFBgY=',
        'CQABAwIDCQEEBgU=',
        'DAIJAAEDAwQGBQ==',
        'AwABCQABCQIECQMEAwUGBgc=',
        'DAAMAgMBAwkABQMEBgYH',
        'CQABCQACAwMECQEFBgY=',
        'AwECDAMJAAEDBAUGBg==',
        'DAIDAQMJAAQGBQ==',
        'DAAJAgMDAQQJAAUGBg==',
        'DAAMAgMBAwMEBQkABgYH',
        'DAADAQMGBA==',
        'DAADAAIJAwQDAQUGBg==',
        'AwABAwIDCQEEBgU=',
        'BgE=',
        'AwACCQABCQEDAwQFBgY=',
        'CQECAwADCQEEBgU=',
        'AwACCQEDBgQ=',
        'DAEDAAIDAwQJAQUGBg==',
        'AwACDAMJAAEDBAUGBg==',
        'DAIDAAMJAQQGBQ==',
        'DAEJAgMDAAQJAQUGBg==',
        'DAEMAgMAAwMEBQkBBgYH',
        'CQABBgM=',
        'AwABAwIDCQABCQQFBgY=',
        'DAADAAIJAwQDAQUJAAYGBw==',
        'DAADAQMJAAQGBQ==',
        'DAAMAQMCAwMEBQYG',
        'DAAJAQMDAgQGBQ==',
        'CQACCQECAwMEBgU=',
        'DAADAgMJAAQDAQUJBAYGBw==',
        'DAEDAgMGBA==',
        'DAADAQIDAwQJAgUGBg==',
        'AwABCQECCQIDAwQFBgY=',
        'CQACAwEDCQIEBgU=',
        'DAEJAAIDAwQGBQ==',
        'AwABCQACCQEECQMEAwUGBgc=',
        'AwECDAMJAAIDBAUGBg==',
        'DAEDAgMJAAQGBQ==',
        'DAAMAQMCAwkABQMEBgYH',
        'CQABCQACAwMECQIFBgY=',
        'DAAJAQMDAgQJAAUGBg==',
        'DAAMAQMCAwMEBQkABgYH',
        'DAADAgMGBA==',
        'DAADAAEJAwQDAgUGBg==',
        'AwABCQACCQIDAwQFBgY=',
        'CQECAwADCQIEBgU=',
        'AwABDAMDAgQGBQ==',
        'BgI=',
        'AwABCQIDBgQ=',
        'DAIDAAEDAwQJAgUGBg==',
        'AwABDAMJAAIDBAUGBg==',
        'DAEDAAMJAgQGBQ==',
        'CQACBgM=',
        'AwABDAMDAgQJAAUGBg==',
        'DAEJAgMDAAQJAgUGBg==',
        'DAEMAgMAAwMEBQkCBgYH',
        'DAADAAEJAwQDAgUJAAYGBw==',
        'DAADAgMJAAQGBQ==',
        'DAAJAQIDAwQGBQ==',
        'AwABCQACCQIDAwQFCQEGBgc=',
        'AwACDAMJAQIDBAUGBg==',
        'DAADAgMJAQQGBQ==',
        'AwABDAMJAQIDBAUGBg==',
        'DAADAQMJAgQGBQ==',
        'CQECBgM=',
        'AwABDAMDAgQJAQUGBg==',
        'AwABDAMDAgQJAAEJBQYGBw==',
        'CQABCQIDBgQ=',
        'DAADAQMJAAIJBAUGBg==',
        'AwABDAMJAAIDBAUJAQYGBw==',
        'DAADAgMJAAEJBAUGBg==',
        'AwACDAMJAAEDBAUJAgYGBw==',
        'DAEMAgMAAwwFAwQGCQMHBgg=',
        'DAAJAQIDAwQJAAUGBg==',
        'DAAMAQMCBAkBBQMDBgYH',
        'CQABCQECAwMECQIFBgY=',
        'DAAJAQMDAgQJAQUGBg==',
        'DAAMAQMCAwMEBQkBBgYH',
        'DAAJAgMDAQQJAgUGBg==',
        'DAAMAgMBAwMEBQkCBgYH',
        'DAADAQIDAwQJAQIJBQYGBw==',
        'DAEDAgMJAQQGBQ==',
        'DAEDAgMJAAEJBAUGBg==',
        'AwECDAMJAAEDBAUJAgYGBw==',
        'DAAMAgMBAwwFAwQGCQMHBgg=',
        'DAEJAAIDAwQJAQUGBg==',
        'DAAMAQMCAwwFAwQGCQMHBgg=',
        'DAIJAAEDAwQJAgUGBg==',
        'DAAJAQMJAgMDBAUMBgYH',
        'DAAMAQwCAwMEAwUGDAcGCA==',
        'DAAMAQwCAwMEAwUGBgc=',
        'DAAJAQMJAgMDBAUGBg==',
        'DAAMAgkBAwMEBQYG',
        'DAADAgMMBAkBAwMFBgYH',
        'DAAMAQkCAwMEBQYG',
        'DAADAQMMBAkCAwMFBgYH',
        'DAADAAEJAgMJAQUJBAUDBgcGCA==',
        'DAEMAgMDBAkABQYG',
        'DAEMAgMDBAYF',
        'DAEDAAEJAgMJAwQDBQYGBw==',
        'DAAMAgMBAwwFAwQGBgc=',
        'DAIJAAMDAQQJAwUGBg==',
        'DAAMAQMCAwwFAwQGBgc=',
        'DAEJAAMDAgQJAwUGBg==',
        'DAAJAQMJAgMDBAUJAAYGBw==',
        'DAAMAQwCAwMEAwUGCQAHBgg=',
        'DAAMAQkCBAMDBQYG',
        'DAEDAAMMBAkCAwMFBgYH',
        'DAADAAEJAQIJAwQDBQYJAwcGCA==',
        'DAAMAgMDBAkBBQYG',
        'DAADAAEMBAkBAgMFBgkDBwYI',
        'DAAMAQMDBAkCBQYG',
        'DAAJAQIJAwQGBQ==',
        'DAADAAEMBAMCBQkBAwkGBwYI',
        'DAEDAAEMBAMCBQkDBgYH',
        'DAEJAgMGBA==',
        'DAAMAgMBAwkEBQYG',
        'DAIDAAEMBAMDBQkBBgYH',
        'DAAMAQMCAwkEBQYG',
        'DAEDAAIMBAMDBQkCBgYH',
        'DAEDAAEJAAIJAgQDBQYJAwcGCA==',
        'DAAJAQIDAwQMBQYG',
        'DAAMAgMDBAYF',
        'DAADAAEJAgMJAwQDBQYGBw==',
        'DAAMAgMAAQkDBQMEBgYH',
        'DAIJAQMDAAQJAwUGBg==',
        'DAADAAEMBAMCBQkDBgYH',
        'DAAJAgMGBA==',
        'DAADAAEJAgMJBAUGBg==',
        'DAIDAAEMBAMDBQkABgYH',
        'DAIDAAEMBAMDBQYG',
        'DAIDAAEJAwQGBQ==',
        'DAIGAw==',
        'DAIDAAEDAgQJAwUGBg==',
        'DAIJAQIDAAQJAwUGBg==',
        'DAIDAQMJAgQDAAUJAwYGBw==',
        'DAADAAEJAwQDAgUMBgYH',
        'DAADAgMMBAYF',
        'DAAMAQMCAwMEBQkDBgYH',
        'DAAJAQMDAgQJAwUGBg==',
        'DAAJAAIJAQIDBAUJAwYGBw==',
        'DAAMAQwCAwMEAwUGCQEHBgg=',
        'DAAMAQMCBAkDBQYG',
        'DAADAQIMBAMDBQkCBgYH',
        'DAADAAEJAQIJAgQDBQYJAwcGCA==',
        'DAEJAAIDAwQMBQYG',
        'DAIJAAIDAQQJAwUGBg==',
        'DAIDAAMJAgQDAQUJAwYGBw==',
        'DAAMAgMBAgMDBQkEBgYH',
        'DAEDAgMMBAYF',
        'DAAMAQMCAwkABQMEBgkDBwYI',
        'CQACCQECAwMEDAUGBg==',
        'DAAJAQMDAgQMBQYG',
        'DAAMAQMCAwMEBQwGBgc=',
        'DAAMAQMDBAYF',
        'DAADAAIJAQMJAwQDBQYGBw==',
        'DAADAAEDAgQJAQMJBQYGBw==',
        'DAAJAQMGBA==',
        'DAAMAQMAAgkDBQMEBgYH',
        'DAEJAgMDAAQJAwUGBg==',
        'DAADAAIJAQMJBAUGBg==',
        'DAEDAAIMBAMDBQkABgYH',
        'DAEDAAIMBAMDBQYG',
        'DAEDAAIJAwQGBQ==',
        'DAEJAQIDAAQJAwUGBg==',
        'DAEDAgMJAQQDAAUJAwYGBw==',
        'DAEGAw==',
        'DAEDAAEDAgQJAwUGBg==',
        'DAADAAIJAwQDAQUMBgYH',
        'DAADAQMMBAYF',
        'DAAMAQMBAgkEBQMDBgYH',
        'DAAJAgMDAQQJAwUGBg==',
        'DAAMAgMBBAkDBQYG',
        'DAADAQIMBAMDBQkBBgYH',
        'DAAJAAEJAQIDBAUJAwYGBw==',
        'DAAMAQwCAwMEAwUGCQIHBgg=',
        'DAADAAIJAQIJAQQDBQYJAwcGCA==',
        'DAIJAAEDAwQMBQYG',
        'DAEJAAEDAgQJAwUGBg==',
        'DAEDAAMJAQQDAgUJAwYGBw==',
        'DAAMAgMBAwkABQMEBgkDBwYI',
        'CQABCQECAwMEDAUGBg==',
        'DAAMAQMBAgMDBQkEBgYH',
        'DAEDAQIJAwQGBQ==',
        'DAAJAgMDAQQMBQYG',
        'DAAMAgMBAwMEBQwGBgc=',
        'DAADAQIMBAMDBQYG',
        'DAADAQIJAwQGBQ==',
        'DAAJAAIDAQQJAwUGBg==',
        'DAADAgMJAAQDAQUJAwYGBw==',
        'DAAJAAEDAgQJAwUGBg==',
        'DAADAQMJAAQDAgUJAwYGBw==',
        'DAEMAgMAAwkBBQMEBgkDBwYI',
        'CQABCQACAwMEDAUGBg==',
        'DAAJAAEJAAIDBAUJAwYGBw==',
        'AwABDAMJAAEJAwUDAgYJBAcGCA==',
        'DAADAQMJAAQDAgUMBgYH',
        'CQABAwIDDAQGBQ==',
        'DAADAgMJAAQDAQUMBgYH',
        'CQACAwEDDAQGBQ==',
        'AwECDAMGBA==',
        'DAADAQIDAwQMBQYG',
        'DAAGAw==',
        'DAADAAEDAgQJAwUGBg==',
        'DAAMAgMAAQMEBQkDBgYH',
        'DAADAAEJAwQGBQ==',
        'DAAMAQMAAgMEBQkDBgYH',
        'DAADAAIJAwQGBQ==',
        'DAAJAQIDAAQJAwUGBg==',
        'DAEMAgMAAwMEBQwGBgc=',
        'DAEDAgMJAQQDAAUMBgYH',
        'CQECAwADDAQGBQ==',
        'AwACDAMGBA==',
        'DAEDAAIDAwQMBQYG',
        'AwABDAMGBA==',
        'DAIDAAEDAwQMBQYG',
        'AwABAwIDDAQGBQ==',
        'DAAJAAMGBA==',
    ]))

_db._data\
    [0][1]\
    [frozenset(logical.every)]\
    [frozenset(logical.every)]\
    = records(map(base64.standard_b64decode, [
        'AAYA',
        'CwYA',
    ]))

_db._data\
    [1][1]\
    [frozenset(logical.every)]\
    [frozenset(logical.every)]\
    = records(map(base64.standard_b64decode, [
        'AQAGAQ==',
        'BgA=',
        'DAAGAQ==',
        'EQAGAQ==',
    ]))

_db._data\
    [2][1]\
    [frozenset(logical.every)]\
    [frozenset(logical.every)]\
    = records(map(base64.standard_b64decode, [
        'AgABBgI=',
        'AwABBgI=',
        'BAABBgI=',
        'BQABBgI=',
        'BwABBgI=',
        'CAABBgI=',
        'CQABBgI=',
        'CgABBgI=',
        'DQABBgI=',
        'DgABBgI=',
        'DwABBgI=',
        'EAABBgI=',
        'EgABBgI=',
        'EwABBgI=',
        'FAABBgI=',
        'FQABBgI=',
    ]))

_db._data\
    [2][2]\
    [frozenset(logical.every)]\
    [frozenset(logical.every)]\
    = records(map(base64.standard_b64decode, [
        'AQAGAgYC',
        'AgABAwABBgIGAw==',
        'AgABAwABBgMGAg==',
        'AwABBgIGAg==',
        'AgABBAABBgIGAw==',
        'AQAGAgYA',
        'BAABCQACBgMGAg==',
        'AwABBgIGAA==',
        'AgABBAABBgMGAg==',
        'BAABCQACBgIGAw==',
        'AQAGAAYC',
        'AwABBgAGAg==',
        'BAABBgIGAg==',
        'BAABBgIGAA==',
        'BAABBgAGAg==',
        'BgAGAA==',
        'BwABBwECBgMGAg==',
        'AQAGAgYB',
        'BwABCQECBgMGAg==',
        'AwABBgIGAQ==',
        'AgABCQABBgIGAw==',
        'CgABAgABBgMGAg==',
        'CQABBAACBgMGAg==',
        'CgABAwABBgMGAg==',
        'BwABBAABBgMGAg==',
        'BAABBgIGAQ==',
        'BwABBgAGAg==',
        'BgAGAQ==',
        'CQABBwECBgMGAg==',
        'CgABBwECBgMGAg==',
        'CQABBgAGAg==',
        'CgABBgAGAg==',
        'BwABBwECBgIGAw==',
        'BwABCQECBgIGAw==',
        'AQAGAQYC',
        'AwABBgEGAg==',
        'BwABBAABBgIGAw==',
        'BwABBgIGAA==',
        'BAABBgEGAg==',
        'BgEGAA==',
        'AgABCQABBgMGAg==',
        'CQABBAACBgIGAw==',
        'CgABAgABBgIGAw==',
        'CgABAwABBgIGAw==',
        'CQABBwECBgIGAw==',
        'CQABBgIGAA==',
        'CgABBwECBgIGAw==',
        'CgABBgIGAA==',
        'BwABBgIGAg==',
        'BwABBgIGAQ==',
        'BwABBgEGAg==',
        'BgEGAQ==',
        'BwABCQABBgIGAw==',
        'CgABBwABBgMGAg==',
        'CQABBgEGAg==',
        'CgABBgEGAg==',
        'BwABCQABBgMGAg==',
        'CQABBgIGAQ==',
        'CgABBwABBgIGAw==',
        'CgABBgIGAQ==',
        'CQABBgIGAg==',
        'CgABCQABBgMGAg==',
        'CgABCQABBgIGAw==',
        'CgABBgIGAg==',
        'AgABDQABBgIGAw==',
        'DgABAgABBgMGAg==',
        'DQABAwABBgMGAg==',
        'DgABAwABBgMGAg==',
        'DAEOAQIGAwYC',
        'EAABAgABBgMGAg==',
        'DAEEAAIGAwYC',
        'EAABDgECBgMGAg==',
        'DQABDgECBgMGAg==',
        'DgABDQECBgMGAg==',
        'DQABBgAGAg==',
        'DgABBgAGAg==',
        'DAEEAAEGAwYC',
        'EAABBAABBgMGAg==',
        'DAEGAAYC',
        'EAABBgAGAg==',
        'DAAOAAIGAwYC',
        'AgABEwABBgIGAw==',
        'DAAEAQIGAwYC',
        'AwABDgACBgIGAw==',
        'AgABFAABBgIGAw==',
        'FQABDAIGAwYC',
        'AwABDAIGAgYD',
        'FQABAwABBgMGAg==',
        'DAANAQIGAwYC',
        'BAABDAIGAgYD',
        'DAAGAAYC',
        'EwABBgAGAg==',
        'BAABDgACBgIGAw==',
        'FQABBAABBgMGAg==',
        'FAABBgAGAg==',
        'EQAGAAYC',
        'BwABDgACBgIGAw==',
        'DgABBwABBgMGAg==',
        'DQABBgEGAg==',
        'DgABBgEGAg==',
        'DAEHAAEGAwYC',
        'BwABDAIGAgYD',
        'DAEGAQYC',
        'EAABBgEGAg==',
        'DQABCQABBgMGAg==',
        'DgABDAIGAwYC',
        'CgABDAIGAgYD',
        'DgABCgABBgMGAg==',
        'DAEOAAIGAwYC',
        'EAABCQABBgMGAg==',
        'DAEKAAEGAwYC',
        'CgABDgACBgIGAw==',
        'DAAHAAEGAwYC',
        'BwABEwABBgIGAw==',
        'DAAGAQYC',
        'EwABBgEGAg==',
        'BwABDgECBgIGAw==',
        'BwABFQABBgIGAw==',
        'FAABBgEGAg==',
        'EQAGAQYC',
        'DAAOAQIGAwYC',
        'CQABEAECBgIGAw==',
        'DAAKAAEGAwYC',
        'CgABDgECBgIGAw==',
        'CQABFAABBgIGAw==',
        'FQABCQABBgMGAg==',
        'CgABFAABBgIGAw==',
        'CgABFQABBgIGAw==',
        'AgABDQABBgMGAg==',
        'DQABAwABBgIGAw==',
        'DgABAgABBgIGAw==',
        'DgABAwABBgIGAw==',
        'DQABDgECBgIGAw==',
        'DQABBgIGAA==',
        'DgABDQECBgIGAw==',
        'DgABBgIGAA==',
        'DAEOAQIGAgYD',
        'DAEEAAIGAgYD',
        'EAABAgABBgIGAw==',
        'EAABDgECBgIGAw==',
        'DAEEAAEGAgYD',
        'DAEGAgYA',
        'EAABBAABBgIGAw==',
        'EAABBgIGAA==',
        'BwABDgACBgMGAg==',
        'DQABBgIGAQ==',
        'DgABBwABBgIGAw==',
        'DgABBgIGAQ==',
        'DQABCQABBgIGAw==',
        'CgABDAIGAwYC',
        'DgABDAIGAgYD',
        'DgABCgABBgIGAw==',
        'DAEHAAEGAgYD',
        'DAEGAgYB',
        'BwABDAIGAwYC',
        'EAABBgIGAQ==',
        'DAEOAAIGAgYD',
        'DAEKAAEGAgYD',
        'EAABCQABBgIGAw==',
        'CgABDgACBgMGAg==',
        'DAAOAAIGAgYD',
        'DAAEAQIGAgYD',
        'AgABEwABBgMGAg==',
        'AwABDgACBgMGAg==',
        'DAANAQIGAgYD',
        'DAAGAgYA',
        'BAABDAIGAwYC',
        'EwABBgIGAA==',
        'AgABFAABBgMGAg==',
        'AwABDAIGAwYC',
        'FQABDAIGAgYD',
        'FQABAwABBgIGAw==',
        'BAABDgACBgMGAg==',
        'FAABBgIGAA==',
        'FQABBAABBgIGAw==',
        'EQAGAgYA',
        'DAAHAAEGAgYD',
        'DAAGAgYB',
        'BwABEwABBgMGAg==',
        'EwABBgIGAQ==',
        'DAAOAQIGAgYD',
        'DAAKAAEGAgYD',
        'CQABEAECBgMGAg==',
        'CgABDgECBgMGAg==',
        'BwABDgECBgMGAg==',
        'FAABBgIGAQ==',
        'BwABFQABBgMGAg==',
        'EQAGAgYB',
        'CQABFAABBgMGAg==',
        'CgABFAABBgMGAg==',
        'FQABCQABBgIGAw==',
        'CgABFQABBgMGAg==',
        'DQABBgIGAg==',
        'DgABBwACBgMGAg==',
        'DgABBwACBgIGAw==',
        'DgABBgIGAg==',
        'DAEHAAIGAwYC',
        'EAABBwACBgMGAg==',
        'DAEOAAEGAwYC',
        'DgABCgACBgIGAw==',
        'DAEHAAIGAgYD',
        'DAEOAAEGAgYD',
        'EAABBwACBgIGAw==',
        'DgABCgACBgMGAg==',
        'DAEGAgYC',
        'DAEKAAIGAgYD',
        'DAEKAAIGAwYC',
        'EAABBgIGAg==',
        'DAAHAQIGAwYC',
        'DQABCgECBgIGAw==',
        'DAAOAAEGAwYC',
        'DgABCgECBgIGAw==',
        'DQABFAABBgIGAw==',
        'FQABDQABBgMGAg==',
        'DgABFAABBgIGAw==',
        'DgABFQABBgIGAw==',
        'DAAMAQYDBgI=',
        'DAEUAAIGAgYD',
        'DAAQAAEGAwYC',
        'EAABEwABBgIGAw==',
        'DAEUAAEGAgYD',
        'DAEKAQIGAgYD',
        'EAABCQECBgIGAw==',
        'FQABEAABBgMGAg==',
        'DAAHAQIGAgYD',
        'DAAOAAEGAgYD',
        'DQABCgECBgMGAg==',
        'DgABCgECBgMGAg==',
        'DAAMAQYCBgM=',
        'DAAQAAEGAgYD',
        'DAEUAAIGAwYC',
        'EAABEwABBgMGAg==',
        'DQABFAABBgMGAg==',
        'DgABFAABBgMGAg==',
        'FQABDQABBgIGAw==',
        'DgABFQABBgMGAg==',
        'DAEUAAEGAwYC',
        'EAABCQECBgMGAg==',
        'DAEKAQIGAwYC',
        'FQABEAABBgIGAw==',
        'DAAGAgYC',
        'DAAKAQIGAgYD',
        'DAAKAQIGAwYC',
        'EwABBgIGAg==',
        'DAAUAAEGAgYD',
        'DAAKAAIGAgYD',
        'FAABCQACBgMGAg==',
        'FQABEwABBgMGAg==',
        'DAAUAAEGAwYC',
        'FAABCQACBgIGAw==',
        'DAAKAAIGAwYC',
        'FQABEwABBgIGAw==',
        'FAABBgIGAg==',
        'FQABFAABBgMGAg==',
        'FQABFAABBgIGAw==',
        'EQAGAgYC',
    ]))

_db._data\
    [3][1]\
    [frozenset(logical.every)]\
    [frozenset(logical.every)]\
    = records(map(base64.standard_b64decode, [
        'AQAGAw==',
        'AwABAwIDBgQ=',
        'AwABBwIDBgQ=',
        'AwABBgM=',
        'AwACBwEDBgQ=',
        'AwACBgM=',
        'CQECAwADBgQ=',
        'DQECBAADBgQ=',
        'BAABBwIDBgQ=',
        'CQECBAADBgQ=',
        'BAACBgM=',
        'EAECAwADBgQ=',
        'BAABBgM=',
        'BAECBAADBgQ=',
        'AwECBAADBgQ=',
        'BgA=',
        'AwECBwADBgQ=',
        'AwECBgM=',
        'CQACAwEDBgQ=',
        'DQACBAEDBgQ=',
        'CQABAwIDBgQ=',
        'DQABBAIDBgQ=',
        'AwABCQIDDQABBAQFBgY=',
        'AwABCQABAwIECQMFBgY=',
        'CQABCQACAwMEBgU=',
        'CQECDQABDQMEBgU=',
        'EAECEAADCQIEBgU=',
        'AwECBAACCQMEBgU=',
        'BAECCQABBwMEBgU=',
        'AwECBAABCQMEBgU=',
        'AwECCQADBgQ=',
        'AwECCgADBgQ=',
        'BAECBwADBgQ=',
        'CQACBAEDBgQ=',
        'BAECBgM=',
        'EAACAwEDBgQ=',
        'CQABCQACBAMEBgU=',
        'CQACDQABDQMEBgU=',
        'EAACEAEDCQIEBgU=',
        'AwACBAECCQMEBgU=',
        'CQABBwIDBgQ=',
        'AwABCQIDDQABDQQFBgY=',
        'DQABDQIDBgQ=',
        'AwABBAIDDQABDQQFBgY=',
        'AwECCQABBwMEBgU=',
        'BAECCQADBgQ=',
        'AwECDQABDQMEBgU=',
        'BAECCgADBgQ=',
        'BwABBgM=',
        'BAACBAEDBgQ=',
        'AwACBAEDBgQ=',
        'BgE=',
        'BAACCQABBwMEBgU=',
        'AwACEAABEAMEBgU=',
        'AwACCQEDBgQ=',
        'AwACCgEDBgQ=',
        'AwACCQABBwMEBgU=',
        'BAACCQEDBgQ=',
        'AwACDQABDQMEBgU=',
        'BAACCgEDBgQ=',
        'CQABBgM=',
        'AwACBAEDCQAEBgU=',
        'BAACBAEDCQAEBgU=',
        'CgABBgM=',
        'EAACDQEDBgQ=',
        'CQABBAIDBgQ=',
        'CQABCQACBwMEBgU=',
        'CQABDQACDQMEBgU=',
        'BwECBgM=',
        'EAABAwIDBgQ=',
        'EAABEAIDCQEEBgU=',
        'AwABEAECEAMEBgU=',
        'CQACBwEDBgQ=',
        'AwACCQEDDQACDQQFBgY=',
        'AwECCQACBwMEBgU=',
        'EAECDgADBgQ=',
        'DQACDQEDBgQ=',
        'AwACBAEDDQACDQQFBgY=',
        'AwECDQACDQMEBgU=',
        'EAECEAADBgQ=',
        'BwACBgM=',
        'BAABBAIDBgQ=',
        'BAABCQACBwMEBgU=',
        'AwABEAACEAMEBgU=',
        'AwABBAIDBgQ=',
        'BgI=',
        'AwABCQIDBgQ=',
        'AwABCgIDBgQ=',
        'AwABCQACBwMEBgU=',
        'BAABCQIDBgQ=',
        'CQACBgM=',
        'AwABBAIDCQAEBgU=',
        'AwABDQACDQMEBgU=',
        'BAABCgIDBgQ=',
        'BAABBAIDCQAEBgU=',
        'CgACBgM=',
        'CQECBwADBgQ=',
        'AwECCQADDQECDQQFBgY=',
        'AwACCQECBwMEBgU=',
        'EAACDgEDBgQ=',
        'AwABCQECBwMEBgU=',
        'EAABDgIDBgQ=',
        'CQECBgM=',
        'AwABBAIDCQEEBgU=',
        'AwABBAIDCQABCQQFBgY=',
        'CQABCQIDBgQ=',
        'DQABDgIDBgQ=',
        'AwABBAIDDQABDgQFBgY=',
        'DQACDgEDBgQ=',
        'AwACBAEDDQACDgQFBgY=',
        'BAABCQECCgMEBgU=',
        'CQECCgADBgQ=',
        'DQECDQADBgQ=',
        'AwECBAADDQECDQQFBgY=',
        'AwACDQECDQMEBgU=',
        'EAACEAEDBgQ=',
        'AwABDQECDQMEBgU=',
        'EAABEAIDBgQ=',
        'EAABAwIDCQEEBgU=',
        'CgECBgM=',
        'DQECDgADBgQ=',
        'AwECBAADDQECDgQFBgY=',
        'BAECCQACCgMEBgU=',
        'CQACCgEDBgQ=',
        'EAACEAEDCQAEBgU=',
        'CQABCgIDBgQ=',
        'CQABCQACCgMEBgU=',
        'DQABEAIDBgQ=',
        'DQABBwIDBgQ=',
        'CQABCQACDQMEBgU=',
        'CQABDQIDBgQ=',
        'EAACEAEDDgAEBgU=',
        'CQACDQEDBgQ=',
        'BAECCQACDQMEBgU=',
        'AwECBAADDQECCQQFBgY=',
        'DQECCQADBgQ=',
        'DQECBgM=',
        'EAABAwIDDgEEBgU=',
        'EAABBwIDBgQ=',
        'AwABDQECCQMEBgU=',
        'EAACBwEDBgQ=',
        'AwACDQECCQMEBgU=',
        'AwECBAADDQECCgQFBgY=',
        'DQECCgADBgQ=',
        'CQECDQADBgQ=',
        'BAABCQECDQMEBgU=',
        'AwACBAEDDQACCQQFBgY=',
        'DQACCQEDBgQ=',
        'AwABBAIDDQABCQQFBgY=',
        'DQABCQIDBgQ=',
        'CQABDgIDBgQ=',
        'AwABBAIDCQABDgQFBgY=',
        'AwABBAIDDgEEBgU=',
        'DgECBgM=',
        'EAABCQIDBgQ=',
        'AwABCQECEAMEBgU=',
        'EAACCQEDBgQ=',
        'AwACCQECEAMEBgU=',
        'AwECCQADDQECCgQFBgY=',
        'CQECEAADBgQ=',
        'DQACBgM=',
        'BAABBAIDDgAEBgU=',
        'BAABDQIDBgQ=',
        'AwABDQACCQMEBgU=',
        'AwABBAIDDgAEBgU=',
        'DgACBgM=',
        'BAABDgIDBgQ=',
        'AwABCQACEAMEBgU=',
        'AwABDQIDBgQ=',
        'AwABDgIDBgQ=',
        'DAIGAw==',
        'AwABEwIDBgQ=',
        'AwABEAACBwMEBgU=',
        'BAABCQACEAMEBgU=',
        'BAABEwIDBgQ=',
        'EAACBgM=',
        'EAECBwADBgQ=',
        'AwECDQACCQMEBgU=',
        'AwACBAEDDQACCgQFBgY=',
        'DQACCgEDBgQ=',
        'EAECCQADBgQ=',
        'AwECCQACEAMEBgU=',
        'AwACCQEDDQACCgQFBgY=',
        'CQACEAEDBgQ=',
        'AwABEAECBwMEBgU=',
        'EAABEAIDDgEEBgU=',
        'EAABFAIDBgQ=',
        'EAECBgM=',
        'CQABDQACCgMEBgU=',
        'CQABCQACEAMEBgU=',
        'CQABEwIDBgQ=',
        'EAACCgEDBgQ=',
        'DQABBgM=',
        'BAACBAEDDgAEBgU=',
        'AwACBAEDDgAEBgU=',
        'DgABBgM=',
        'BAACDQEDBgQ=',
        'AwACDQABCQMEBgU=',
        'BAACDgEDBgQ=',
        'AwACCQABEAMEBgU=',
        'AwACDQEDBgQ=',
        'AwACDgEDBgQ=',
        'AwACEAABBwMEBgU=',
        'BAACCQABEAMEBgU=',
        'DAEGAw==',
        'AwACEwEDBgQ=',
        'BAACEwEDBgQ=',
        'EAABBgM=',
        'BAECDQADBgQ=',
        'AwECDQABCQMEBgU=',
        'BAECDgADBgQ=',
        'AwECCQABEAMEBgU=',
        'AwABBAIDDQABCgQFBgY=',
        'DQABCgIDBgQ=',
        'AwABCQIDDQABCgQFBgY=',
        'CQABEAIDBgQ=',
        'AwACBAECDQMEBgU=',
        'EAACEAEDDgIEBgU=',
        'CQACDQABCgMEBgU=',
        'CQABCQACEwMEBgU=',
        'EAACFAEDBgQ=',
        'EwECBgM=',
        'CQACEwEDBgQ=',
        'BAECEAADBgQ=',
        'AwECDQADBgQ=',
        'AwECDgADBgQ=',
        'AwECBAABDQMEBgU=',
        'BAECCQABEAMEBgU=',
        'AwECBAACDQMEBgU=',
        'EAECEAADDgIEBgU=',
        'CQECDQABCgMEBgU=',
        'CQABCQACFAMEBgU=',
        'AwABCQABAwIEDQMFBgY=',
        'AwABCQIDDQABEwQFBgY=',
        'DQABEwIDBgQ=',
        'CQABFAIDBgQ=',
        'DQACEwEDBgQ=',
        'CQACFAEDBgQ=',
        'FAECBgM=',
        'AwECEAADBgQ=',
        'DAAGAw==',
        'AwECEwADBgQ=',
        'BAECEwADBgQ=',
        'EwABBgM=',
        'EAECFAADBgQ=',
        'EwACBgM=',
        'CQECEwADBgQ=',
        'BAABEAIDBgQ=',
        'DQECEwADBgQ=',
        'CQECFAADBgQ=',
        'FAACBgM=',
        'AwACEAEDBgQ=',
        'FAABBgM=',
        'AwABEAIDBgQ=',
        'AwABFAIDBgQ=',
        'EQAGAw==',
    ]))

class circuitdb(dict):
    """
    Wrapper class for a circuit data set that contains an (arbitrary but fixed)
    example of the smallest possible logical circuit (in terms of the number of
    unary and/or binary gates) for each possible logical function (from a finite
    set of functions). This class supports both a dictionary-like interface
    (inherited from the :obj:`dict` type) and a function-like interface (via the
    :obj:`__call__` method).

    **Logical Function Representation:** Logical functions are represented using
    tuples in an identical manner to that of the :obj:`~logical.logical.logical`
    class defined in the `logical <https://pypi.org/project/logical/>`_ library. For
    example, the logical function *f* (*x*, *y*, *z*) = *x* **and** *y* **and** *z*
    (*i.e.*, three-argument conjunction) is represented using a tuple representation
    of the output column of the truth table for the function (assuming that the
    possible inputs are in ascending dictionary order): ``(0, 0, 0, 0, 0, 0, 0, 1)``.

    >>> circuitdb((0, 0, 0, 0, 0, 0, 0, 1)).gate.to_legible()
    (('id',), ('id',), ('id',), ('and', 0, 1), ('and', 2, 3), ('id', 4))

    For logical functions having multiple outputs, the entries in the tuple may
    themselves be tuples. For example, *f* (*x*, *y*) = (*y*, *x*) is represented
    using the tuple ``((0, 0), (1, 0), (0, 1), (1, 1))``.

    >>> circuitdb(((0, 0), (1, 0), (0, 1), (1, 1))).gate.to_legible()
    (('id',), ('id',), ('id', 1), ('id', 0))

    **Circuit Representation:** Retrieved circuits are instances of the
    :obj:`~circuit.circuit.circuit` class that is defined in the
    `circuit <https://pypi.org/project/circuit/>`_ library. In order to make this
    documentation human-readible, the examples include an invocation of the
    :obj:`~circuit.circuit.gates.to_legible` method belonging to the gate list
    associated with the returned :obj:`~circuit.circuit.circuit` object. This
    representation of a circuit consists of a list of unary and binary gates. Each
    gate is represented as a tuple. The first entry in each gate tuple is the name
    of the logical function corresponding to that gate (as defined in the
    :obj:`~logical.logical.logical.names` class attribute in the
    `logical <https://pypi.org/project/logical/>`_ library). The remaining
    entries in the gate tuple are the indices of the input gates to that gate.

    >>> circuitdb((0, 0, 0, 0, 0, 0, 0, 1)).gate.to_legible()
    (('id',), ('id',), ('id',), ('and', 0, 1), ('and', 2, 3), ('id', 4))

    In the circuit above, the entry ``('and', 2, 3)`` represents a gate that
    is a conjunction of the gates at positions ``2`` and ``3`` in the overall list
    (*i.e.* , ``('id',)`` and ``('and', 0, 1)``).

    **Set of Permitted Gates:** For any given logical function, it is possible to
    construct a corresponding circuit using a variety of gate sets. For each logical
    function, the database contains an example of a smallest circuit for each of a
    small collection of sets of unary and binary gates. The set of gates that can be
    used to construct a circuit can be supplied using the ``operators`` parameter.
    In the remaining examples below, circuits are retrieved for the specific function
    ``(0, 0, 1, 0, 0, 0, 0, 1)``. The unary and binary logical operators represented
    by the gates in the circuit below are drawn from the set of permitted gates
    ``{logical.id_, logical.not_, logical.and_, logical.or_}``.

    >>> from logical import logical
    >>> for g in circuitdb(
    ...     (0, 0, 1, 0, 0, 0, 0, 1),
    ...     frozenset([logical.id_, logical.not_, logical.and_, logical.or_])
    ... ).gate.to_legible():
    ...     print(g)
    ('id',)
    ('id',)
    ('id',)
    ('and', 0, 2)
    ('or', 0, 2)
    ('not', 4)
    ('or', 3, 5)
    ('and', 1, 6)
    ('id', 7)

    All gates in the circuit below are found in the set
    ``{logical.id_, logical.not_, logical.and_, logical.xor_}``.

    >>> for g in circuitdb(
    ...     (0, 0, 1, 0, 0, 0, 0, 1),
    ...     frozenset([logical.id_, logical.not_, logical.and_, logical.xor_])
    ... ).gate.to_legible():
    ...     print(g)
    ('id',)
    ('id',)
    ('id',)
    ('not', 0)
    ('xor', 2, 3)
    ('and', 1, 4)
    ('id', 5)

    By default (or if the set of *all* gates is supplied using the constant
    :obj:`~logical.logical.logical.every` that is defined in the
    `logical <https://pypi.org/project/logical/>`_), a smallest circuit that can
    be built using *any* combination of unary or binary gates is returned.

    >>> circuitdb((0, 0, 1, 0, 0, 0, 0, 1)).gate.to_legible()
    (('id',), ('id',), ('id',), ('xor', 0, 2), ('nimp', 1, 3), ('id', 4))
    >>> circuitdb((0, 0, 1, 0, 0, 0, 0, 1), logical.every).gate.to_legible()
    (('id',), ('id',), ('id',), ('xor', 0, 2), ('nimp', 1, 3), ('id', 4))

    **Set of Gates to Minimize:** Multiple possible circuits that use gates from
    a given gate set can be used to implement a logical function. Some of these
    circuits may have more of one type of gate than other circuits. Thus, there
    is an option to specify using the ``minimize`` parameter *which* gates *do*
    contribute to the *size* of the circuit (*i.e.*, the metric that is being
    minimized). All other gates are *not counted* for the purposes of comparing
    circuits according to their size.

    >>> for g in circuitdb(
    ...     (0, 0, 1, 0, 0, 0, 0, 1),
    ...     frozenset([logical.id_, logical.not_, logical.and_, logical.xor_]), {logical.and_}
    ... ).gate.to_legible():
    ...     print(g)
    ('id',)
    ('id',)
    ('id',)
    ('not', 0)
    ('xor', 2, 3)
    ('and', 1, 4)
    ('id', 5)

    **Supported Combinations:** Each logical function has a number of input values,
    a number of output values, a set of permitted gates/**operators**, and a set of
    gates to **minimize** in quantity. Entries exist in the database for only a finite
    set of logical functions. The table below lists the supported combinations of
    function input count, function output count, and gate set that are found in the
    database. **All** functions for a given combination of inputs and outputs are
    supported (*e.g.*, all ``2**(2**3) = 256`` functions having three inputs and one
    output are supported). Gate sets are defined using operator constants found in
    the `logical <https://pypi.org/project/logical/>`_ library).

    +------------+-------------+-----------------------------+----------------------------+
    | **inputs** | **outputs** | **operators**               | **minimize**               |
    +------------+-------------+-----------------------------+----------------------------+
    | 1          | 1           | ``{id_, not_, and_, or_}``  | ``{id_, not_, and_, or_}`` |
    +------------+-------------+-----------------------------+----------------------------+
    | 1          | 1           | ``{id_, not_, and_, xor_}`` | ``{and_}``                 |
    +------------+-------------+-----------------------------+----------------------------+
    | 1          | 1           | ``every``                   | ``every``                  |
    +------------+-------------+-----------------------------+----------------------------+
    | 2          | 1           | ``{id_, not_, and_, or_}``  | ``{id_, not_, and_, or_}`` |
    +------------+-------------+-----------------------------+----------------------------+
    | 2          | 1           | ``{id_, not_, and_, xor_}`` | ``{and_}``                 |
    +------------+-------------+-----------------------------+----------------------------+
    | 2          | 1           | ``every``                   | ``every``                  |
    +------------+-------------+-----------------------------+----------------------------+
    | 2          | 2           | ``{id_, not_, and_, or_}``  | ``{id_, not_, and_, or_}`` |
    +------------+-------------+-----------------------------+----------------------------+
    | 2          | 2           | ``{id_, not_, and_, xor_}`` | ``{and_}``                 |
    +------------+-------------+-----------------------------+----------------------------+
    | 2          | 2           | ``every``                   | ``every``                  |
    +------------+-------------+-----------------------------+----------------------------+
    | 3          | 1           | ``{id_, not_, and_, or_}``  | ``{id_, not_, and_, or_}`` |
    +------------+-------------+-----------------------------+----------------------------+
    | 3          | 1           | ``{id_, not_, and_, xor_}`` | ``{and_}``                 |
    +------------+-------------+-----------------------------+----------------------------+
    | 3          | 1           | ``every``                   | ``every``                  |
    +------------+-------------+-----------------------------+----------------------------+

    The database supports retrieval using index notation, as well.

    >>> circuitdb[1][1][frozenset(logical.every)][frozenset(logical.every)][(0, 0)].gate.to_legible()
    (('id',), ('uf', 0), ('id', 1))
    >>> circuitdb[1][1][frozenset(logical.every)][frozenset(logical.every)][((0,), (0,))].gate.to_legible()
    (('id',), ('uf', 0), ('id', 1))

    The top-level database instance has keys that represent to the number of
    inputs of the logical function. The second level down, the keys represent
    the number of outputs of a logical function. The third level down, keys
    represent the set of unary or binary gates to which circuits are restricted.
    Finally, the last level down, the keys represent logical functions.

    >>> list(sorted(list(circuitdb.keys()))) == [0, 1, 2, 3]
    True
    >>> ks = list(sorted(list(circuitdb[1][1].keys())))
    >>> ks[0] == frozenset({logical.and_, logical.or_, logical.not_, logical.id_})
    True
    >>> circuitdb[2][1][ks[0]][ks[0]][(1,1,1,1)].gate.to_legible()
    (('id',), ('id',), ('not', 0), ('or', 0, 2), ('id', 3))

    Note that the internal representation organizes the circuits by arity.

    >>> _d = {i: _db._data[i][1] for i in range(1,4)}
    >>> all(len(_d[1][o][m]) == 4 for o in _d[1] for m in _d[1][o])
    True
    >>> all(len(_d[2][o][m]) == 16 for o in _d[2] for m in _d[2][o])
    True
    >>> all(len(_d[3][o][m]) == 256 for o in _d[3] for m in _d[3][o])
    True
    """
    def __call__(
        self: circuitdb, truthtable: tuple, operators: set = None, minimize: set = None
    ) -> circuit.circuit:
        """
        Function-like interface for the circuit database, with user-friendly
        defaults for retrieving circuit data.

        By supplying a logical function (represented as a tuple), it is possible
        to retrieve a smallest circuit that implements that function. Logical
        functions having one output are represented using a tuple of
        integers (or booleans), or a tuple of one-element tuples.

        >>> circuitdb((0, 0)).gate.to_legible()
        (('id',), ('uf', 0), ('id', 1))
        >>> circuitdb(((0,), (0,))).gate.to_legible()
        (('id',), ('uf', 0), ('id', 1))
        >>> circuitdb((False, False)).gate.to_legible()
        (('id',), ('uf', 0), ('id', 1))

        A logical function having a vector of two outputs is represented using
        a tuple of two-element tuples.

        >>> circuitdb(((1, 0), (1, 0), (1, 0), (0, 1))).gate.to_legible()
        (('id',), ('id',), ('and', 0, 1), ('not', 2), ('id', 3), ('id', 2))

        It is also possible to retrieve a smallest circuit that only uses gates
        from a specific set of gates.

        >>> circuitdb(
        ...     (0, 0, 0, 0, 0, 0, 0, 0),
        ...     [logical.id_, logical.not_, logical.and_, logical.or_]
        ... ).gate.to_legible()
        (('id',), ('id',), ('id',), ('not', 0), ('and', 0, 3), ('id', 4))

        Any attempt to access the data with a malformed key raises an
        exception.

        >>> circuitdb([0, 0, 0, 0])
        Traceback (most recent call last):
          ...
        TypeError: truth table must be a tuple
        >>> circuitdb((0, 0, 0))
        Traceback (most recent call last):
          ...
        ValueError: truth table must have a length that is a power of two
        >>> circuitdb(('abc', 'xyz'))
        Traceback (most recent call last):
          ...
        TypeError: truth table must contain boolean values, integers in the range [0, 1], or tuples of such
        >>> circuitdb((('abc', 'xyz')))
        Traceback (most recent call last):
          ...
        TypeError: truth table must contain boolean values, integers in the range [0, 1], or tuples of such
        >>> circuitdb(((1, 'abc'), (1, 0), (1, 0), (0, 1)))
        Traceback (most recent call last):
          ...
        TypeError: truth table must contain boolean values, integers in the range [0, 1], or tuples of such
        >>> circuitdb(((), ()))
        Traceback (most recent call last):
          ...
        ValueError: truth table entries must each represent at least one value
        >>> circuitdb(((), (1, 0)))
        Traceback (most recent call last):
          ...
        ValueError: truth table entries must all have the same length
        >>> circuitdb((0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
        Traceback (most recent call last):
          ...
        ValueError: no entries for functions of arity 4
        >>> circuitdb(((0,0,0), (1,1,1)))
        Traceback (most recent call last):
          ...
        ValueError: no entries for functions of arity 1 having output vectors of length 1
        >>> circuitdb((0, 0, 0, 0, 0, 0, 0, 0), 132)
        Traceback (most recent call last):
          ...
        TypeError: collection of operators must be a set, frozenset, list, or tuple
        >>> circuitdb((0, 0, 0, 0, 0, 0, 0, 0), 132)
        Traceback (most recent call last):
          ...
        TypeError: collection of operators must be a set, frozenset, list, or tuple
        >>> circuitdb((0, 0, 0, 0, 0, 0, 0, 0), [(0, 1, 0)])
        Traceback (most recent call last):
          ...
        ValueError: collection of operators must only contain valid operators
        >>> circuitdb((0, 0, 0, 0, 0, 0, 0, 0), [(0, 1)])
        Traceback (most recent call last):
          ...
        ValueError: no entries for functions of arity 3 that have only the specified operators
        >>> id_not_and_or = [logical.id_, logical.not_, logical.and_, logical.or_]
        >>> circuitdb((0, 0, 0, 0, 0, 0, 0, 0), id_not_and_or, 123)
        Traceback (most recent call last):
          ...
        TypeError: collection of operators the number of which to minimize must be a set, frozenset, list, or tuple
        >>> circuitdb((0, 0, 0, 0, 0, 0, 0, 0), id_not_and_or, [(0, 1, 0)])
        Traceback (most recent call last):
          ...
        ValueError: collection of operators the number of which to minimize must contain only valid operators
        >>> circuitdb((0, 0, 0, 0, 0, 0, 0, 0), id_not_and_or, [(0, 1)])
        Traceback (most recent call last):
          ...
        ValueError: no entries for functions of arity 3 for specified operators and minimization criteria

        Additional exhaustive tests are presented below.

        >>> from itertools import product
        >>> evals = lambda c, a: tuple([c.evaluate(v)[0] for v in product(*[[0, 1]]*a)])
        >>> _d = {i: _db._data[i][1] for i in range(1,4)}
        >>> aoms = [(a, o, m) for a in _d for o in _d[a] for m in _d[a][o]]
        >>> all(all(t == evals(circuitdb(t, o, m), a) for t in product(*[[0, 1]]*(2**a))) for (a, o, m) in aoms)
        True
        >>> evals = lambda c, a: tuple([tuple(c.evaluate(v)) for v in product(*[[0, 1]]*a)])
        >>> aoms = [(a, o, m) for a in [2] for o in _db._data[a][2] for m in _db._data[a][2][o]]
        >>> pairs = [(0, 0), (0, 1), (1, 0), (0, 1)]
        >>> all(all(t == evals(circuitdb(t, o, m), a) for t in product(*[pairs]*(2**a))) for (a, o, m) in aoms)
        True
        """
        # Ensure the function truth table is a tuple.
        if not isinstance(truthtable, tuple):
            raise TypeError('truth table must be a tuple')

        # Ensure that the function truth table has valid entry types.
        if all(isinstance(e, tuple) for e in truthtable):
            if not all(all(b in [0, 1, False, True] for b in e) for e in truthtable):
                raise TypeError('truth table must contain boolean values, integers in the range [0, 1], or tuples of such')
        elif not all(e in [0, 1, False, True] for e in truthtable):
            raise TypeError('truth table must contain boolean values, integers in the range [0, 1], or tuples of such')

        # Determine the arity of the function represented by the truth table.
        arity = int(math.log2(len(truthtable)))

        # Check that the number of entries in the truth table is a power of two.
        if len(truthtable) < 1 or 2**arity != len(truthtable):
            raise ValueError('truth table must have a length that is a power of two')

        # Determine the number of outputs in the truth table (and check it is consistent).
        coarity = 1
        if all(isinstance(e, tuple) for e in truthtable):
            ls = set(len(e) for e in truthtable)
            if len(ls) == 1:
                coarity = list(ls)[0]
                if coarity < 1:
                    raise ValueError('truth table entries must each represent at least one value')
                elif coarity == 1: # Convert tuple of singleton tuples into simple tuple.
                    truthtable = tuple(e[0] for e in truthtable)
            else:
                raise ValueError('truth table entries must all have the same length')

        # Ensure that data for functions of the requested arity and coarity is available.
        if arity not in _db._data:
            raise ValueError('no entries for functions of arity ' + str(arity))

        if coarity not in _db._data[arity]:
            raise ValueError(
                'no entries for functions of arity ' + str(arity) + ' ' +\
                'having output vectors of length ' + str(arity)
            )

        # Normalize the truth table representation.
        if coarity == 1:
            truthtable = tuple(map(int, truthtable))
        else:
            truthtable = tuple(tuple(map(int, e)) for e in truthtable)

        # Allow all operators by default or check that data is present for given operators.
        operators = frozenset(logical.every) if operators is None else operators

        if not isinstance(operators, (set, frozenset, list, tuple)):
            raise TypeError('collection of operators must be a set, frozenset, list, or tuple')

        if not frozenset(operators).issubset(logical.every):
            raise ValueError('collection of operators must only contain valid operators')

        if frozenset(operators) not in _db._data[arity][1]:
            raise ValueError(
                'no entries for functions of arity ' + str(arity) + ' ' +\
                'that have only the specified operators'
            )

        # Minimize the total number of operators of any available kind by default.
        minimize_ = list(sorted(list(_db._data[arity][1][frozenset(operators)].keys())))[0]
        minimize = minimize_ if minimize is None else minimize

        # Check that the operators to minimize are valid and corresponding data exists.
        if not isinstance(minimize, (set, frozenset, list, tuple)):
            raise TypeError(
                'collection of operators the number of which to minimize ' +\
                'must be a set, frozenset, list, or tuple'
            )

        if not frozenset(minimize).issubset(logical.every):
            raise ValueError(
                'collection of operators the number of which to minimize ' +\
                'must contain only valid operators'
            )

        if frozenset(minimize) not in _db._data[arity][1][frozenset(operators)]:
            raise ValueError(
                'no entries for functions of arity ' + str(arity) + ' ' +\
                'for specified operators and minimization criteria'
            )

        # The bracket notation below is overloaded in the :obj:`records.__getitem__` method,
        # so there is no risk of users modifying the data.
        return _db._data[arity][coarity][frozenset(operators)][frozenset(minimize)][truthtable]

# Exported object with function-like and dictionary-like interfaces
# hides the class definition that is used to construct it.
if os.environ.get("CIRCUITDB_DOCS") != "1":
    circuitdb_ = circuitdb
    circuitdb = circuitdb_(_db._data)

if __name__ == "__main__":
    doctest.testmod() # pragma: no cover
