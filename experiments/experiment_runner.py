import argparse
import sys
import os
import yaml
import logging
from datetime import datetime

# Define project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

from src.scraper.driver import setup_driver
from src.scraper import GoogleEngine, BingEngine, YahooEngine
from src.evaluation import Evaluator
from src.utils.io_utils import read_queries_set, add_query_result

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

def load_config(config_path):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def resolve_path(path):
    """
    Resolve a path relative to the project root if it is not absolute.
    """
    if os.path.isabs(path):
        return path
    return os.path.join(PROJECT_ROOT, path)

def run_scraper(config, limit=None):
    logging.info("Starting Scraper...")
    
    # Override limit if provided in args
    cfg_limit = limit if limit else config['experiment']['limit']
    
    timestamp = datetime.now().strftime(config['experiment']['timestamp_format'])
    
    # Resolve output directory
    output_base_dir = resolve_path(config['paths']['output_task1'])
    output_dir = os.path.join(output_base_dir, timestamp)
    
    # Resolve assets directory
    assets_dir = resolve_path(config['paths']['assets'])
    queries_file = os.path.join(assets_dir, '100QueriesSet2.txt')
    
    queries = read_queries_set(queries_file)
    
    # Initialize Engines
    engines = {
        "Google": GoogleEngine(config['search_engines']['Google'], cfg_limit, config['experiment']['min_delay'], config['experiment']['max_delay']),
        "Bing": BingEngine(config['search_engines']['Bing'], cfg_limit, config['experiment']['min_delay'], config['experiment']['max_delay']),
        "Yahoo!": YahooEngine(config['search_engines']['Yahoo!'], cfg_limit, config['experiment']['min_delay'], config['experiment']['max_delay'])
    }
    
    driver = setup_driver(config['experiment']['headless_mode'], config['experiment']['user_agent'])

    try:
        for engine_name, engine in engines.items():
            logging.info(f"--- SWITCHING TO ENGINE: {engine_name} ---")
            
            for idx, query in enumerate(queries):
                logging.info(f"[{idx + 1}/{len(queries)}] Searching {engine_name}: {query}")
                
                results = engine.search(query, driver)
                add_query_result(output_dir, engine_name, query, results)
                
                logging.info(f"Found {len(results)} links.")
                
    except KeyboardInterrupt:
        logging.info("Scraper interrupted.")
    finally:
        driver.quit()
        logging.info("Scraping Done.")

def run_evaluation(config):
    logging.info("Starting Evaluation...")
    
    task1_dir = resolve_path(config['paths']['output_task1'])
    task2_dir = resolve_path(config['paths']['output_task2'])
    
    evaluator = Evaluator(task1_dir, task2_dir)
    evaluator.run()
    logging.info("Evaluation Done.")

if __name__ == "__main__":
    default_config = os.path.join(PROJECT_ROOT, "config", "experiment.yaml")

    parser = argparse.ArgumentParser(description="SearchRank Analytics Engine Experiment Runner")
    parser.add_argument("--task", choices=["scrape", "evaluate", "all"], default="all", help="Task to run")
    parser.add_argument("--config", default=default_config, help="Path to configuration file")
    parser.add_argument("--limit", type=int, help="Limit number of results per query (overrides config)")
    
    args = parser.parse_args()
    
    config = load_config(args.config)
    
    if args.task in ["scrape", "all"]:
        run_scraper(config, args.limit)
        
    if args.task in ["evaluate", "all"]:
        run_evaluation(config)
