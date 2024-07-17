"""

Decompress BPE:
This module adapts the de-compression algorithm
written by TheFlyingZamboni for his awesome tool LoDModS.
Thanks a lot mate for this one!.
--------------------------------------------------------------------------------------------------------------
Input file:  = Binary Animation BPE'd Data BYTES
--------------------------------------------------------------------------------------------------------------
:RETURN: -> self.decoded_bpe = {Decompressed Animation Binary Data}
--------------------------------------------------------------------------------------------------------------
Copyright (C) 2024 DooMMetaL

"""

class BpeFile:
    def __init__(self, binary_data_bpe=dict) -> None:
        self.binary_data_bpe = binary_data_bpe
        self.decoded_bpe: bytes = b''
        self.decompress_bpe()

    def decompress_bpe(self) -> None:
        """
        Decompresses LoD's BPE-compressed files.
        LoD compresses some files using a form of blocked byte-pair encoding
        algorithm. The original data is compressed in blocks of up to 0x800
        decompressed bytes. Each compressed block is composed of a 4-byte header
        specifying the size of the decompressed block, instructions for filling
        out a byte-pair dictionary, and the compressed data.
        Decompression works by reading bytes as instructions for building the
        byte-pair dictionary, filling it out until the offset exceeds the
        dictionary size (256 bytes). Once the dictionary is filled out, bytes
        are read as compressed data, and either added to the list of decompressed
        data (if it is a real value) or used to get the corresponding byte-pair
        value until their are no more bytes left in the compressed block.
        Parameters
        ----------
        compressed_file : BufferedReader
            I/O file object of compressed file.
        start_block : int
            Data block to start decompression from. (default: 0)
        end_block : int
            Data block to decompress up to (non-inclusive). (default: 512)
        is_subfile : bool
            Flag indicating whether file is a BPE file, or a non-BPE file
            that contains BPE-compressed data within its body. (default: False)
        """
        start_block = 0
        end_block = 512
        block = -1
        if end_block <= start_block:
            """Decompress: End block is not greater than start block. '
                'Decompressing through end of file"""
            end_block = 512
        decompressed_file_offset = 0
        blocksize_list = []
        decompressed_byte_list = [] # Decompressed BPE FILE
        archive_offset = 8
        while True:
            block += 1
            # Each block is preceded by 4-byte int up to 0x800 giving the number
            # of decompressed bytes in the block. 0x00000000 indicates that there
            # are no further blocks and decompression is complete.
            bytes_remaining_in_block = self.binary_data_bpe[archive_offset : (archive_offset + 4)]
            archive_offset += 4
            if bytes_remaining_in_block == b'\x00\x00\x00\x00'\
                    or bytes_remaining_in_block == b'':
                break
            elif int.from_bytes(bytes_remaining_in_block, 'little') > 0x800:
                """('Decompress: 0x%s at offset 0x%08x is an invalid block size' %
                    (bytes_remaining_in_block.hex(), compressed_file.tell()-4))
                ('Decompress: Skipping file')"""
                return print('Decompress: Skipping file')
            # If the routine has not reached the specified starting block, just
            # increment the decompressed file offset. If it's between start and
            # end, add the block size to the list of block sizes. Break the loop
            # once the end block is passed.
            if start_block > block:
                decompressed_file_offset += int.from_bytes(bytes_remaining_in_block, 'little')
            elif start_block <= block < end_block:
                blocksize_list.append(bytes_remaining_in_block)
            else:
                break
            bytes_remaining_in_block = int.from_bytes(bytes_remaining_in_block, 'little')
            # Build the initial dictionary/lookup table. The left-character dict
            # is filled so that each key contains itself as a value, while the
            # right-character dict is filled with empty values.
            dict_leftch = {x: x for x in range(0x100)}
            dict_rightch = {x: '' for x in range(0x100)}
            # Build adaptive dictionary.
            key = 0x00
            while key < 0x100:  # Dictionary is 256 bytes long. Loop until all keys filled.
                # If byte_pairs_to_read is >=0x80, then only the next byte will
                # be read into the dictionary, placed at the index value calculated
                # using the below formula. Otherwise, the byte indicates how many
                # sequential bytes to read into the dictionary.
                byte_pairs_to_read = int.from_bytes(self.binary_data_bpe[archive_offset: (archive_offset + 1)], 'big')
                archive_offset += 1
                if byte_pairs_to_read >= 0x80:
                    key = key - 0x7f + byte_pairs_to_read
                    byte_pairs_to_read = 0
                else:
                    byte_pairs_to_read = byte_pairs_to_read
                # For each byte/byte pair to read, read the next byte and add it
                # to the leftch dict at the current key. If the character matches
                # the key it's at, increment key and continue. If it does not,
                # read the next character and add it to the same key in the
                # rightch dict before incrementing key and continuing.
                if key < 0x100:  # Check that dictionary length not exceeded.
                    for i in range(byte_pairs_to_read+1):
                        compressed_byte = int.from_bytes(self.binary_data_bpe[archive_offset: (archive_offset + 1)], 'big')
                        archive_offset += 1
                        dict_leftch[key] = compressed_byte

                        if compressed_byte != key:
                            compressed_byte = int.from_bytes(self.binary_data_bpe[archive_offset: (archive_offset + 1)], 'big')
                            archive_offset += 1
                            dict_rightch[key] = compressed_byte
                        key += 1
            # Decompress block
            # On each pass, read one byte and add it to a list of unresolved bytes.
            while bytes_remaining_in_block > 0:
                compressed_byte = int.from_bytes(self.binary_data_bpe[archive_offset: (archive_offset + 1)], 'big')
                archive_offset += 1
                unresolved_byte_list = [compressed_byte]
                # Pop the first item in the list of unresolved bytes. If the
                # byte key == value in dict_leftch, append it to the list of
                # decompressed bytes. If the byte key != value in dict_leftch,
                # insert the leftch followed by rightch to the unresolved byte
                # list. Loop until the unresolved byte list is empty.
                while unresolved_byte_list:
                    compressed_byte = unresolved_byte_list.pop(0)
                    if compressed_byte == dict_leftch[compressed_byte]:
                        if block >= start_block:
                            decompressed_byte_list.append(compressed_byte.to_bytes(1, 'big'))
                        bytes_remaining_in_block -= 1
                    else:
                        unresolved_byte_list.insert(0, dict_rightch[compressed_byte])
                        unresolved_byte_list.insert(0, dict_leftch[compressed_byte])
            if archive_offset % 4 != 0:  # Word-align the pointer.
                archive_offset = archive_offset + 4 - archive_offset % 4
        archive_offset += 4
        join_byte_array = b''.join(decompressed_byte_list)
        self.decoded_bpe = join_byte_array