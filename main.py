from pipeline.mosaic_tiles import MosaicTiles
from pipeline.clip_states import ClipStates 
from pipeline.analyze_loss import AnalyzeLoss
from utils.log import get_logger

log = get_logger()

def main():
    # Step 1: Mosaic Tiles
    mosaic = MosaicTiles()
    raster_files = mosaic.find_tiles()
    log.info(f'Found {len(raster_files)} raster files for processing.')
    # mosaic.create_mosaic(raster_files)

    # Step 2: Clip Rasters to States
    clipper = ClipStates()
    clipper.clip_rasters_to_states()

    # Step 3: Analyze Forest Loss by State
    analyzer = AnalyzeLoss()
    analyzer.analyze_loss_by_state()

if __name__ == "__main__":
    main()