import json
from argparse import Namespace

from caelestia.utils.scheme import (
    Scheme,
    get_scheme,
    get_scheme_flavours,
    get_scheme_modes,
    get_scheme_names,
    scheme_variants,
)
from caelestia.utils.theme import apply_colours


class Set:
    args: Namespace

    def __init__(self, args: Namespace) -> None:
        self.args = args

    def run(self) -> None:
        scheme = get_scheme()

        if self.args.notify:
            scheme.notify = True

        if self.args.random:
            scheme.set_random()
            apply_colours(scheme.colours, scheme.mode)
        elif self.args.name or self.args.flavour or self.args.mode or self.args.variant:
            if self.args.name:
                scheme.name = self.args.name
            if self.args.flavour:
                scheme.flavour = self.args.flavour
            if self.args.mode:
                scheme.mode = self.args.mode
            if self.args.variant:
                scheme.variant = self.args.variant
            apply_colours(scheme.colours, scheme.mode)
        else:
            print("No args given. Use --name, --flavour, --mode, --variant or --random to set a scheme")


class Get:
    args: Namespace

    def __init__(self, args: Namespace) -> None:
        self.args = args

    def run(self) -> None:
        scheme = get_scheme()

        if self.args.name or self.args.flavour or self.args.mode or self.args.variant:
            if self.args.name:
                print(scheme.name)
            if self.args.flavour:
                print(scheme.flavour)
            if self.args.mode:
                print(scheme.mode)
            if self.args.variant:
                print(scheme.variant)
        else:
            print(scheme)


class List:
    args: Namespace

    def __init__(self, args: Namespace) -> None:
        self.args = args

    def run(self) -> None:
        multiple = [self.args.names, self.args.flavours, self.args.modes, self.args.variants].count(True) > 1

        if self.args.names or self.args.flavours or self.args.modes or self.args.variants:
            if self.args.names:
                if multiple:
                    print("Names:", *get_scheme_names())
                else:
                    print("\n".join(get_scheme_names()))
            if self.args.flavours:
                if multiple:
                    print("Flavours:", *get_scheme_flavours())
                else:
                    print("\n".join(get_scheme_flavours()))
            if self.args.modes:
                if multiple:
                    print("Modes:", *get_scheme_modes())
                else:
                    print("\n".join(get_scheme_modes()))
            if self.args.variants:
                if multiple:
                    print("Variants:", *scheme_variants)
                else:
                    print("\n".join(scheme_variants))
        else:
            current_scheme = get_scheme()
            schemes = {}
            for scheme in get_scheme_names():
                schemes[scheme] = {}
                for flavour in get_scheme_flavours(scheme):
                    s = Scheme(
                        {
                            "name": scheme,
                            "flavour": flavour,
                            "mode": current_scheme.mode,
                            "variant": current_scheme.variant,
                            "colours": current_scheme.colours,
                        }
                    )
                    modes = get_scheme_modes(scheme, flavour)
                    if s.mode not in modes:
                        s._mode = modes[0]
                    try:
                        s.refresh_colours()
                        schemes[scheme][flavour] = s.colours
                    except ValueError:
                        pass

            print(json.dumps(schemes))


class Preview:
    args: Namespace

    def __init__(self, args: Namespace) -> None:
        self.args = args

    def run(self) -> None:
        requested = (
            self.args.name,
            self.args.flavour,
            self.args.mode,
            self.args.variant,
        )
        if not any(value is not None for value in requested):
            print("No args given. Use --name, --flavour, --mode, or --variant to preview a scheme")
            return

        current = get_scheme()

        # Name is independent
        name = self.args.name if self.args.name is not None else current.name
        if name not in get_scheme_names():
            raise ValueError(f'Invalid scheme name: "{name}"')

        # Flavours depend on the selected name
        valid_flavours = get_scheme_flavours(name)
        if self.args.flavour is not None:
            if self.args.flavour not in valid_flavours:
                raise ValueError(
                    f'Invalid flavour "{self.args.flavour}" for scheme "{name}". Valid flavours: {valid_flavours}'
                )
            flavour = self.args.flavour
        else:
            flavour = current.flavour if current.flavour in valid_flavours else valid_flavours[0]

        # Modes depend on both name and flavour
        valid_modes = get_scheme_modes(name, flavour)
        if self.args.mode is not None:
            if self.args.mode not in valid_modes:
                raise ValueError(
                    f'Scheme "{name} {flavour}" does not have a "{self.args.mode}" mode. Valid modes: {valid_modes}'
                )
            mode = self.args.mode
        else:
            mode = current.mode if current.mode in valid_modes else valid_modes[0]

        # Variant is independent of name/flavour/mode
        variant = self.args.variant if self.args.variant is not None else current.variant
        if variant not in scheme_variants:
            raise ValueError(f'Invalid scheme variant: "{variant}"')

        preview = Scheme(
            {
                "name": name,
                "flavour": flavour,
                "mode": mode,
                "variant": variant,
                "colours": current.colours.copy(),
            }
        )
        preview.notify = self.args.notify
        preview.refresh_colours()

        print(json.dumps(preview.to_dict()))
