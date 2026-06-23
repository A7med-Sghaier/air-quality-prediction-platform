import sys, os
from air_pollution.cli.extractors.history_extractor import HistoryExtractor
from air_pollution.cli.extractors.station_extractor import StationExtractor
from air_pollution.cli.predictors.noise_predictor import NoisePredictors
from air_pollution.cli.preprocess.preprocessor import Preprocessor
from datetime import datetime, timedelta
from air_pollution.common.metric_evaluators import MeanAbsoluteErrorEvaluator, MeanAbsolutePercentageErrorEvaluator, \
    MaximumPercentageErrorEvaluator, RootMeanSquaredErrorEvaluator, MeanSquaredErrorEvaluator
from dateutil.parser import parse


class BColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def submit_predictors():
    submits_source = str(os.getcwd()) + "/air_pollution/api/submission/sample_submission_aq.csv"

    predictors = NoisePredictors(submits_source)
    predictors.mean_predictor()

    # submitter = PredictorSubmitter()
    # submitter.submit(submits_source)


def extract_history(argv):
    if len(argv) < 3:
        print(BColors.FAIL + 'Please provide a city name!' + BColors.ENDC)
        print_help()
        return

    days = 1
    if len(argv) >= 4:
        days = int(argv[3])

    previous_n_date = (datetime.now() - timedelta(days=days)).date()
    previous_date = (datetime.now() - timedelta(days=1)).date()

    date_begin = str(previous_n_date) + "-0"
    date_end = str(previous_date) + "-23"

    city_id = 'ld' if argv[2].lower() == 'london' else 'bj'

    history_extractor = HistoryExtractor(city_id)
    history_extractor.persist_histories(history_extractor.extract_air_quality_data(date_begin, date_end), 'aq')
    history_extractor.persist_histories(history_extractor.extract_meteorology_data(date_begin, date_end), 'me')
    history_extractor.persist_histories(history_extractor.extract_meteorology_grid_data(date_begin, date_end),
                                        'me_grid')


def calculate_metric(argv):
    if len(argv) < 3:
        print(BColors.FAIL + 'Please provide a predictor name!' + BColors.ENDC)
        print_help()
        return
    if len(argv) < 4:
        print(BColors.FAIL + 'Please provide a metric name!' + BColors.ENDC)
        print_help()
        return
    if len(argv) < 5:
        print(BColors.FAIL + 'Please provide a station name or id!' + BColors.ENDC)
        print_help()
        return

    predictor = argv[2]
    metric_name = argv[3]
    station_name = argv[4]

    from_date = (datetime.now() - timedelta(days=45)) if len(argv) < 6 else parse(argv[5])
    to_date = datetime.now() if len(argv) < 7 else parse(argv[6])

    if metric_name == 'mean-error':
        res = MeanAbsoluteErrorEvaluator().calculate_from_db(station_id=station_name, from_date=from_date,
                                                             to_date=to_date,
                                                             predictor=predictor)
        print(res)
        return

    if metric_name == 'mean-absolute-percentage-error':
        res = MeanAbsolutePercentageErrorEvaluator().calculate_from_db(station_id=station_name, from_date=from_date,
                                                                       to_date=to_date,
                                                                       predictor=predictor)
        print(res)
        return

    if metric_name == 'maximum-percentage-error':
        res = MaximumPercentageErrorEvaluator().calculate_from_db(station_id=station_name, from_date=from_date,
                                                                  to_date=to_date,
                                                                  predictor=predictor)
        print(res)
        return

    if metric_name == 'mean-squared-error':
        res = MeanSquaredErrorEvaluator().calculate_from_db(station_id=station_name, from_date=from_date,
                                                            to_date=to_date,
                                                            predictor=predictor)
        print(res)
        return
    if metric_name == 'root-mean-squared-error':
        res = RootMeanSquaredErrorEvaluator().calculate_from_db(station_id=station_name, from_date=from_date,
                                                                to_date=to_date,
                                                                predictor=predictor)
        print(res)
        return

    print(BColors.FAIL + 'Unknown metric "' + metric_name + '"' + BColors.ENDC)
    print_help()


def preprocess(argv):
    if len(argv) < 3:
        print(BColors.FAIL + 'Please provide a city!' + BColors.ENDC)
        print_help()
        return
    if len(argv) < 4:
        print(BColors.FAIL + 'Please provide how many days you want to preprocess!' + BColors.ENDC)
        print_help()
        return

    if len(argv) < 5:
        days_in_rows = False
    else:
        days_in_rows = True if argv[4] == 'true' else False

    preprcessor = Preprocessor(argv[2], int(argv[3]), days_in_rows)
    preprcessor.preprocess()

    pass


def execute_by_name(name, argv):
    if name == 'extract_stations':
        StationExtractor().create_stations()
        return
    if name == 'extract_history':
        extract_history(argv=argv)
        return
    if name == 'submit_predictors':
        submit_predictors()
        return
    if name == 'metric':
        calculate_metric(argv)
        return
    if name == 'preprocess':
        preprocess(argv=argv)
        return


def print_help():
    print('')
    print('Usage:')
    print('     python console.py <command> [optional: other args...]')
    print('     or')
    print('     pipenv run python console.py <command> [optional: other args...]')
    print('')
    print('A wrapper for all our command line scripts.')
    print('')
    print('Available commands:')
    print('     extract_stations         inserts all stations (london/beijing and station/grid) into the database')
    print('     submit_predictors        submits the current predictors to KDD cup')
    print('     preprocess               preprocesses the data')
    print('          Options:')
    print('               <city_name>    the city you want to preprocess (london/beijing)')
    print('               <days>         How many days do you want to preprocess?')
    print('               <days_in_rows> [Optional] default: false, true | false ')
    print('     extract_history          downloads the current history (from today) and appends it to the stations')
    print('          Options:')
    print('               <city_name>    the city you want to import (london/beijing)')
    print('               <days>         [Optional] default: 1, How many days do you want to import')
    print('     metric                   downloads the current history (from today) and appends it to the stations')
    print('          Options:')
    print('               <predictor>    Name of the predictor we want to evaluate')
    print('               <metric_name>  Name of the metric we want to evaluate')
    print('               <station_id>   The ID or name of the station we want to use')
    print('               <from>         [Optional] default: 1, How many days do you want to import')
    print('               <to>           [Optional] default: 1, How many days do you want to import')


def execute(argv):
    if len(argv) < 2:
        print_help()
        return

    program = argv[1]

    if program == '--help' or program == '-h':
        print_help()
        return

    execute_by_name(program, sys.argv)


if __name__ == '__main__':
    execute(sys.argv)
