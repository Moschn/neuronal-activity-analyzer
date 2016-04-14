from analyzer.loader import Loader, register_loader_class
import analyzer.pillow_loader
import analyzer.bioformat_loader

register_loader_class(analyzer.pillow_loader.PILLoader)
register_loader_class(analyzer.bioformat_loader.BioFormatLoader)
