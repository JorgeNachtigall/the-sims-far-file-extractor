import io
import os
from dataclasses import dataclass
from typing import Union, List


@dataclass
class ManifestEntry:
    length: int
    _length: int
    file_offset: int
    file_name_length: int
    file_name: str


@dataclass
class Manifest:
    number_of_files: int
    manifest_entries: List[ManifestEntry]


def convert_bytes(
    n_bytes: int, type: str, stream: io.BufferedReader
) -> Union[str, int]:
    """Converts a bytearray into a string or an integer.

    Args:
        n_bytes (int): The total number of bytes to convert.
        type (str): The type ('str' or 'int') that the bytes will be converted to.
        stream (io.BufferedReader): The file stream to read from.

    Returns:
        Union[str, int]: The converted value.

    Raises:
        ValueError: If the provided type is not supported.
    """
    byte_array = bytearray(n_bytes)
    stream.readinto(byte_array)

    if type == "str":
        value = byte_array.decode("utf-8")
    elif type == "int":
        value = int.from_bytes(byte_array, "little")
    else:
        raise ValueError("Type not supported.")

    return value


def parse_manifest_entry(stream: io.BufferedReader) -> ManifestEntry:
    """Parses a manifest entry from a file stream.

    Args:
        stream (io.BufferedReader): The file stream to read from.

    Returns:
        ManifestEntry: The parsed ManifestEntry object.
    """
    length = convert_bytes(4, "int", stream)
    _length = convert_bytes(4, "int", stream)
    file_offset = convert_bytes(4, "int", stream)
    file_name_length = convert_bytes(4, "int", stream)
    file_name = convert_bytes(file_name_length, "str", stream).replace("\\", "/")

    return ManifestEntry(
        length=length,
        _length=_length,
        file_offset=file_offset,
        file_name_length=file_name_length,
        file_name=file_name,
    )


def get_manifest_entry_by_name(manifest: Manifest, file_name: str) -> ManifestEntry:
    """Retrieves a manifest entry by the given file name.

    Args:
        manifest (Manifest): The Manifest object to search within.
        file_name (str): The file name to search for.
        stream (io.BufferedReader): The file stream to read from.

    Returns:
        ManifestEntry: The matching ManifestEntry object.

    Raises:
        ValueError: If the file name is not found in the Manifest.
    """
    for entry in manifest.manifest_entries:
        if entry.file_name == file_name:
            return entry

    raise ValueError("File name not found in Manifest.")


def get_bytes(offset: int, length: int, stream: io.BufferedReader) -> bytearray:
    """Reads and returns a specific range of bytes from a file stream.

    Args:
        offset (int): The offset from the beginning of the stream.
        length (int): The number of bytes to read.
        stream (io.BufferedReader): The file stream to read from.

    Returns:
        bytearray: The bytes read from the stream.
    """
    byte_array = bytearray(length)
    stream.seek(offset, io.SEEK_SET)
    stream.readinto(byte_array)

    return byte_array


def extract_manifest_files(
    manifest: Manifest, output_path: str, far_file_path: str
) -> None:
    """Extracts files from a manifest and saves them to the specified output path.

    Args:
        manifest (Manifest): The Manifest object containing the file entries.
        output_path (str): The directory where the extracted files will be saved.
        far_file_path (str): The path to the .far file.

    Returns:
        None
    """
    with open(far_file_path, "rb") as stream:
        for entry in manifest.manifest_entries:
            extract_manifest_entry(entry=entry, output_path=output_path, stream=stream)


def extract_manifest_entry(
    entry: ManifestEntry, output_path: str, stream: io.BufferedReader
) -> None:
    """Extracts a single manifest entry and saves it to the specified output path.

    Args:
        entry (ManifestEntry): The ManifestEntry object to extract.
        output_path (str): The directory where the extracted file will be saved.
        stream (io.BufferedReader): The file stream to read from.

    Returns:
        None
    """
    byte_array = get_bytes(entry.file_offset, length=entry.length, stream=stream)

    file_path = os.path.join(output_path, entry.file_name)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    try:
        with open(file_path, "wb") as output_file:
            output_file.write(byte_array)
    except IOError as error:
        print(f"Error writing to file: {file_path}")
        print(f"Error: {error}")


def create_manifest(far_file_path: str) -> Manifest:
    """Creates a Manifest object by parsing the provided input file.

    Args:
        input_file (str): The path to the input file.

    Returns:
        Manifest: The created Manifest object.
    """
    with open(far_file_path, "rb") as stream:
        signature = convert_bytes(8, "str", stream)
        version = convert_bytes(4, "int", stream)
        manifest_offset = convert_bytes(4, "int", stream)

        stream.seek(manifest_offset, io.SEEK_SET)

        number_of_files = convert_bytes(4, "int", stream)
        manifest_files = list()

        for _ in range(number_of_files):
            manifest_entry = parse_manifest_entry(stream)
            manifest_files.append(manifest_entry)

        manifest = Manifest(number_of_files, manifest_files)

        return manifest
