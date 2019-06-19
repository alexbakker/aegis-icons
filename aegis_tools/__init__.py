import argparse
import getpass
import io
import json
import os
from collections import namedtuple
from qrcode import QRCode
from urllib.parse import urlencode, quote as urlquote

from aegis.icons import IconGenerator
from aegis.vault import decrypt_vault, VaultGenerator

def _write_output(output, data):
    if output != "-":
        with io.open(output, "w") as f:
            f.write(data)
    else:
        print(data)

def _do_icons(args):
    gen = IconGenerator()
    for icon in gen.generate_all():
        with open(os.path.join(args.output, icon.filename), "w") as f:
            f.write(icon.get_xml())

def _do_vault(args):
    gen = VaultGenerator(no_icons=args.no_icons)
    vault = gen.generate(entry_count=args.entries)
    _write_output(args.output, json.dumps(vault, indent=4))

def _do_decrypt(args):
    with io.open(args.input, "r") as f:
        data = json.load(f)

    # ask the user for a password
    password = getpass.getpass()

    db = decrypt_vault(data, password)
    _write_output(args.output, json.dumps(db, indent=4))

def _do_qr(args):
    entry = VaultGenerator(no_icons=True).generate_entry()

    params = {
        "secret": entry["info"]["secret"],
        "issuer": entry["issuer"],
        "algorithm": entry["info"]["algo"],
        "digits": entry["info"]["digits"],
        "period": entry["info"]["period"]
    }
    uri = "otpauth://totp/{}:{}.com?".format(urlquote(entry["name"]), urlquote(entry["issuer"]))

    qr = QRCode()
    qr.add_data(uri + urlencode(params))
    qr.print_ascii(invert=True)

def main():
    parser = argparse.ArgumentParser(description="A collection of developer tools for Aegis Authenticator", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    subparsers = parser.add_subparsers()

    icon_parser = subparsers.add_parser("gen-icons", help="Generate icons for Aegis based on simple-icons")
    icon_parser.add_argument("--output", dest="output", required=True, help="icon output folder")
    icon_parser.set_defaults(func=_do_icons)

    vault_parser = subparsers.add_parser("gen-vault", help="Generate a random vault for use in the Aegis app")
    vault_parser.add_argument("--output", dest="output", default="-", help="vault output file ('-' for stdout)")
    vault_parser.add_argument("--entries", dest="entries", default=20, type=int, help="the amount of entries to generate")
    vault_parser.add_argument("--no-icons", dest="no_icons", action="store_true", help="do not generate entry icons")
    vault_parser.set_defaults(func=_do_vault)

    qr_parser = subparsers.add_parser("gen-qr", help="Generate a random QR code")
    qr_parser.set_defaults(func=_do_qr)

    decrypt_parser = subparsers.add_parser("decrypt-vault", help="Decrypt an Aegis vault")
    decrypt_parser.add_argument("--input", dest="input", required=True, help="encrypted Aegis vault file")
    decrypt_parser.add_argument("--output", dest="output", default="-", help="output file ('-' for stdout)")
    decrypt_parser.set_defaults(func=_do_decrypt)

    args = parser.parse_args()
    if args.func:
        args.func(args)
