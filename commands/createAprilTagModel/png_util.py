"""Adapted from: https://pyokagan.name/blog/2019-10-14-png/.

NOTE: This tool was developed instead of using the Python Pillow module so that we don't
need to install third-party libraries into the Fusion 360 Python environment. 

Using PIL to get the same results would look something like this:

    from PIL import Image with Image.open(png_file, "r") as im:
        width, height = im.size 
        pix_vals = im.load()
"""
import pathlib
import struct
import zlib
from typing import List, Tuple

_BYTES_PER_PIXEL = 4


def read_png(img_path: pathlib.Path) -> Tuple[int, int, List[int]]:
    """Returns the PNG image width and height in pixels."""
    with img_path.open("rb") as f:
        _raise_if_png_not_valid(f)

        chunks = []
        while True:
            chunk_type, chunk_data = read_chunk(f)
            chunks.append((chunk_type, chunk_data))
            if chunk_type == b"IEND":
                break

    _, IHDR_data = chunks[0]  # IHDR is always first chunk
    width, height = _unpack_and_validate_data(IHDR_data)

    IDAT_data = b"".join(
        chunk_data for chunk_type, chunk_data in chunks if chunk_type == b"IDAT"
    )
    IDAT_data = zlib.decompress(IDAT_data)

    Recon = []
    stride = width * _BYTES_PER_PIXEL

    def Recon_a(r, c):
        return Recon[r * stride + c - _BYTES_PER_PIXEL] if c >= _BYTES_PER_PIXEL else 0

    def Recon_b(r, c):
        return Recon[(r - 1) * stride + c] if r > 0 else 0

    def Recon_c(r, c):
        return (
            Recon[(r - 1) * stride + c - _BYTES_PER_PIXEL]
            if r > 0 and c >= _BYTES_PER_PIXEL
            else 0
        )

    i = 0
    for r in range(height):  # for each scanline
        filter_type = IDAT_data[i]  # first byte of scanline is filter type
        i += 1
        for c in range(stride):  # for each byte in scanline
            Filt_x = IDAT_data[i]
            i += 1
            if filter_type == 0:  # None
                Recon_x = Filt_x
            elif filter_type == 1:  # Sub
                Recon_x = Filt_x + Recon_a(r, c)
            elif filter_type == 2:  # Up
                Recon_x = Filt_x + Recon_b(r, c)
            elif filter_type == 3:  # Average
                Recon_x = Filt_x + (Recon_a(r, c) + Recon_b(r, c)) // 2
            elif filter_type == 4:  # Paeth
                Recon_x = Filt_x + PaethPredictor(
                    Recon_a(r, c), Recon_b(r, c), Recon_c(r, c)
                )
            else:
                raise Exception("unknown filter type: " + str(filter_type))
            Recon.append(Recon_x & 0xFF)  # truncation to byte

    pixels = reshape(Recon, height, width)

    return width, height, pixels


def reshape(flat_pixel_values: List[int], height: int, width: int) -> List[List[int]]:
    """Takes a flattened, one-dimensional list of 4-Tuple pixel values and converts to
    a two dimensional array of a singular pixel values.

    Parameters:
        flat_pixel_values: One-dimensional list of pixel values where every four values
        correspond to the 4-Tuple of PNG file pixel values. E.g. for an 8x8 pixel image
        where there are 64 total pixels this list should container 256 values (8 pixels
        * 8 pixels * 4 values per pixel)

        height: height of the PNG in number of pixels.

        width: width of the PNG in numnber of pixels.

    Returns:
        A two-dimensional array formatted as a list of lists where index [x][y]
        corresponds to the black/white (0/255) pixel value at the (x,y) location in the
        original PNG value.

    NOTE: We reduce the 4-Tuple to singular pixel values since we only care about black
    and white PNG files for AprilTags.
    """
    # First reduce the original list of deconstructed 4-Tuples to a list of singular
    # pixel values
    bw_pixel_values = [flat_pixel_values[4 * x] for x in range(height * width)]
    pixels = []
    for i in range(height):
        start = i * width
        end = start + width
        row = bw_pixel_values[start:end]
        pixels.append(row)

    return pixels


def read_chunk(f) -> Tuple:
    chunk_length, chunk_type = struct.unpack(">I4s", f.read(8))
    chunk_data = f.read(chunk_length)
    (chunk_expected_crc,) = struct.unpack(">I", f.read(4))
    chunk_actual_crc = zlib.crc32(
        chunk_data, zlib.crc32(struct.pack(">4s", chunk_type))
    )
    if chunk_expected_crc != chunk_actual_crc:
        raise RuntimeError("chunk checksum failed")
    return chunk_type, chunk_data


def PaethPredictor(a, b, c):
    p = a + b - c
    pa = abs(p - a)
    pb = abs(p - b)
    pc = abs(p - c)
    if pa <= pb and pa <= pc:
        Pr = a
    elif pb <= pc:
        Pr = b
    else:
        Pr = c
    return Pr


def _raise_if_png_not_valid(f):
    _PNG_SIG = b"\x89PNG\r\n\x1a\n"
    if f.read(len(_PNG_SIG)) != _PNG_SIG:
        raise RuntimeError("Invalid PNG Signature")


def _unpack_and_validate_data(IHDR_data):
    width, height, bitd, colort, compm, filterm, interlacem = struct.unpack(
        ">IIBBBBB", IHDR_data
    )
    if compm != 0:
        raise Exception("invalid compression method")
    if filterm != 0:
        raise Exception("invalid filter method")
    if colort != 6:
        raise Exception("we only support truecolor with alpha")
    if bitd != 8:
        raise Exception("we only support a bit depth of 8")
    if interlacem != 0:
        raise Exception("we only support no interlacing")

    return width, height
