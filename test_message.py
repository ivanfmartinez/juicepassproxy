import unittest
from juicebox_message import juicebox_message_from_string, juicebox_message_from_bytes, JuiceboxMessage, JuiceboxEncryptedMessage, JuiceboxCommand
from juicebox_exceptions import JuiceboxInvalidMessageFormat
import codecs
import datetime

class TestMessage(unittest.TestCase):
    def test_message_building(self):
        m = JuiceboxCommand()
        m.time = datetime.datetime(2012, 3, 23, 23, 24, 55, 173504)
        m.offline_amperage = 16
        m.instant_amperage = 20
        self.assertEqual(m.build(), "CMD52324A20M16C006S001!5RE$")
        print(m.inspect())


    def test_message_building_new(self):
        m = JuiceboxCommand(new_version=True)
        m.time = datetime.datetime(2012, 3, 23, 23, 24, 55, 173504)
        m.offline_amperage = 16
        m.instant_amperage = 20
        self.assertEqual(m.build(), "CMD52324A0020M016C006S001!YUK$")
        print(m.inspect())


    def test_entrypted_message(self):
        messages = [
            # https://github.com/snicker/juicepassproxy/issues/73#issuecomment-2149670058
            "303931303034323030313238303636303432373332333632303533353a7630396512b10a000000716b1493270404a809cbcbb7995fd86b391e4b5e606fd5153a81ecd6251eb2bf87da82db9ceaefb268caa8f0c01b538af48e45d1ef3ad28ca72a4fdf05261780fd753b361906368634821bf6cada5624bae11feb7dc975cfe14e2c305eb01adcc7b39687ddc130d66cc39bc2ccac7f903cb9b50adb9a77b95b77bd364b82dcbe8599dc9a8a880cc44eb0f04e8a1d9f4a6305978a7f3e3c58d5"
            "303931303034323030313238303636303432373332333632303533353a7630396512b10a00000073480d38833df8ebed8add322332c5c9f0501b32e9b35b71d1d8d3e389f5b9002b42ee953b5d9f712ddd36ebcb9f0a8973eba739f388583429d3fcd4cd135f9e4d437ad6ad21c11ad8e89369252ada194b52436beeb67a15b4a24f85eae07ebeeb6270588c94e390fa6da00c831e290a8552bd49ce014db1aa70843ebb5db2b0dea0fa20d0ed00714ae3001c895bf54779d5d1449ee15bf486"
            # TODO try to find a message that maybe can be decoded as string if possible
        ]
        for message in messages:
            print("enc")
            m = juicebox_message_from_bytes(codecs.decode(message,'hex'))
            self.assertEqual(JuiceboxEncryptedMessage, type(m))
    
    def test_message_validation(self):
        messages = [
            "g4rbl3d",
        ]
        for message in messages:
            with self.assertRaises(JuiceboxInvalidMessageFormat):
                print(f"bad : {message}")
                m = juicebox_message_from_string(message)


    def test_command_message_parsing(self):
        """
        Command messages are typically sent by the Cloud to the Juicebox
        """
        raw_msg = "CMD41325A0040M040C006S638!5N5$"
        m = juicebox_message_from_string(raw_msg)
        self.assertEqual(m.payload_str, "CMD41325A0040M040C006S638")
        self.assertEqual(m.checksum_str, "5N5")
        self.assertEqual(m.checksum_str, m.checksum_computed())
        self.assertEqual(m.build(), raw_msg)

        self.assertEqual(m.get_value("DOW"), "4")
        self.assertEqual(m.get_value("HHMM"), "1325")

    def test_status_message_parsing(self):
        """
        Status messages are sent by the Juicebox
        """
        raw_msg = "0910042001260513476122621631:v09u,s627,F10,u01254993,V2414,L00004555804,S01,T08,M0040,C0040,m0040,t29,i75,e00000,f5999,r61,b000,B0000000!55M:"

        m = juicebox_message_from_string(raw_msg)
        self.assertEqual(m.payload_str, "0910042001260513476122621631:v09u,s627,F10,u01254993,V2414,L00004555804,S01,T08,M0040,C0040,m0040,t29,i75,e00000,f5999,r61,b000,B0000000")
        self.assertEqual(m.checksum_str, "55M")
        self.assertEqual(m.checksum_str, m.checksum_computed())
        self.assertEqual(m.get_value("C"), "0040")
        self.assertEqual(m.get_value("v"), "09u")
        self.assertEqual(m.get_value("V"), "2414")
        self.assertEqual(m.get_value("serial"), "0910042001260513476122621631")
        self.assertEqual(m.build(), raw_msg)

    def test_message_checksums(self):
        messages = [
            'CMD41325A0040M040C006S638!5N5$', # @MrDrew514 (v09u)
            'CMD62210A20M18C006S006!31Y$',
            'CMD62228A20M15C008S048!IR4$',
            'CMD62207A20M20C244S997!R5Y$',
            'CMD62207A20M20C008S996!ZI4$',
            'CMD62201A20M20C244S981!ECD$',
            'CMD62201A20M20C006S982!QT8$',
            'CMD31353A0000M010C244S741!2B3$', # (v09u)
            # Original message changed to remove real serial number
            '0910000000000000000000000000:v09u,s001,F31,u00412974,V1366,L00004262804,S02,T28,M0024,C0024,m0032,t09,i23,e-0001,f5990,r99,b000,B0000000,P0,E0004501,A00161,p0996!ZW5:'
        ]

        for message in messages:
            m = juicebox_message_from_string(message)
#            print(m.inspect())

            self.assertEqual(m.build(), message)
            self.assertEqual(m.checksum_str, m.checksum_computed())

if __name__ == '__main__':
    unittest.main()