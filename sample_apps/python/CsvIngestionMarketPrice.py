import csv
import time
from Constant import DATABASE_NAME, TABLE_NAME


class CsvIngestionMarketPrice:
    def __init__(self, client):
        self.client = client

    def bulk_write_records(self, filepath):
        with open(filepath, 'r') as csv_file:
            # creating a csv reader object
            csv_reader = csv.reader(csv_file)

            records = []
            current_time = self._current_milli_time()
            counter = 0

            # extracting each data row one by one
            for row in csv_reader:
                dimensions = [
                    {'Name': 'TSType', 'Value': '15'},
                    {'Name': 'TSMapping', 'Value': 'base'},
                    {'Name': 'ObjectId', 'Value': row[0]},
                    {'Name': 'date', 'Value': row[1]}
                ]

                record_time = current_time - (counter * 50)

                record = {
                    'Dimensions': dimensions,
                    'MeasureName': 'marketPrice',
                    'MeasureValueType': 'MULTI',
                    'Time': str(record_time),
                    'MeasureValues': [
                        {
                            'Name': 'open',
                            'Value': row[2],
                            'Type': 'DOUBLE'
                        },
                        {
                            'Name': 'high',
                            'Value': row[3],
                            'Type': 'DOUBLE'
                        },
                        {
                            'Name': 'low',
                            'Value': row[4],
                            'Type': 'DOUBLE'
                        },
                        {
                            'Name': 'close',
                            'Value': row[5],
                            'Type': 'DOUBLE'
                        }
                    ]
                }

                records.append(record)
                counter = counter + 1

                if len(records) == 100:
                    self._submit_batch(records, counter)
                    records = []

            if len(records) != 0:
                self._submit_batch(records, counter)

            print("Ingested %d records" % counter)

    def _submit_batch(self, records, counter):
        try:
            result = self.client.write_records(DatabaseName=DATABASE_NAME, TableName=TABLE_NAME,
                                               Records=records, CommonAttributes={})
            print("Processed [%d] records. WriteRecords Status: [%s]" % (counter,
                                                                         result['ResponseMetadata']['HTTPStatusCode']))
        except Exception as err:
            print("Error:", err)

    @staticmethod
    def _current_milli_time():
        return int(round(time.time() * 1000))
