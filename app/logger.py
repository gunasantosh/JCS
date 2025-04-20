import logging

# Configure the logger globally
logging.basicConfig(
    level=logging.INFO,
    # format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    format="%(message)s"
)

logger = logging.getLogger("app") 
