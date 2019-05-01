import imp
import os

from iopipe import IOpipe

iopipe = IOpipe()
wrapped_handler = None


@iopipe
def wrapper(event, context):
    return get_wrapped_handler()(event, context)


def get_handler():
    if "IOPIPE_HANDLER" not in os.environ or not os.environ["IOPIPE_HANDLER"]:
        raise ValueError("No value specified in IOPIPE_HANDLER environment variable")

    try:
        module_path, handler_name = os.environ["IOPIPE_HANDLER"].rsplit(".", 1)
    except ValueError:
        raise ValueError(
            "Improperly formated handler value: %s" % os.environ["IOPIPE_HANDLER"]
        )

    module_path = module_path.replace("/", ".")
    file_handle, pathname, desc = None, None, None

    try:
        for segment in module_path.split("."):
            if pathname is not None:
                pathname = [pathname]

            file_handle, pathname, desc = imp.find_module(segment, pathname)

        if file_handle is None:
            module_type = desc[2]
            if module_type == imp.C_BUILTIN:
                raise ImportError(
                    "Cannot use built-in module %s as a handler module" % module_path
                )

        module = imp.load_module(module_path, file_handle, pathname, desc)
    except Exception as e:
        raise ImportError("Failed to import module: %s" % module_path)
    finally:
        if file_handle is not None:
            file_handle.close()

    try:
        handler = getattr(module, handler_name)
    except AttributeError as e:
        raise AttributeError("No handler %s in module %s" % (handler_name, module_path))

    return handler


def get_wrapped_handler():
    global wrapped_handler

    if not wrapped_handler:
        wrapped_handler = get_handler()

    return wrapped_handler
