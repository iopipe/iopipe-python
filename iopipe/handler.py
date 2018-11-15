import os

from iopipe import IOpipe

iopipe = IOpipe()
wrapped_handler = None


@iopipe
def wrapper(event, context):
    return get_wrapped_handler()(event, context)


def get_wrapped_handler():
    global wrapped_handler

    if not wrapped_handler:
        if "IOPIPE_HANDLER" not in os.environ or not os.environ["IOPIPE_HANDLER"]:
            raise ValueError(
                "No value specified in IOPIPE_HANDLER environment variable"
            )

        try:
            module_path, handler_name = os.environ["IOPIPE_HANDLER"].rsplit(".", 1)
        except ValueError:
            raise ValueError(
                "Improperly formated handler value: %s" % os.environ["IOPIPE_HANDLER"]
            )

        module_path = module_path.replace("/", ".")

        try:
            module = __import__(module_path)
        except ImportError:
            raise ImportError("Failed to import module: %s" % module_path)

        try:
            wrapped_handler = getattr(module, handler_name)
        except AttributeError:
            raise AttributeError(
                "No handler %s in module %s" % (handler_name, module_path)
            )

    return wrapped_handler
