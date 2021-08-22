import pytest
# run pytest in docker terminal
print("running db tests")


class TestDatabase:
    from mngrs.db_mngr import MongoDataBaseManager
    db_manager = MongoDataBaseManager()
    test_rate = {'EUR': 1}
    def test_mongo_connection(self):
        assert self.db_manager.db.command('ping')

    def test_mongo_exchange_db_write_case(self):
        rate_ts = self.db_manager.set_rates('USD', self.test_rate)
        assert rate_ts, f"Failed set rate test case! No timestamp received: {rate_ts}"
        # delete rates that are saved for the test
        assert self.db_manager.delete_rate(rate_ts)

    def test_mongo_exchange_db_read_case(self):
        rate_db_ts = self.db_manager.set_rates('USD', self.test_rate)
        ts, rate = self.db_manager.get_rates("USD", 1, target_currency="EUR")[0]

        assert rate_db_ts == ts, f"Failed rad rate test case! Set ts for rate is not read ts! " \
                                 f"{rate_db_ts} != {ts}"

    def test_mongo_exchange_db_read_sorted_case(self):
        curr = 1
        rate_db_ts1 = self.db_manager.set_rates('USD', {'EUR': curr})
        if not rate_db_ts1:
            curr += 1
            rate_db_ts1 = self.db_manager.set_rates('USD', {'EUR': curr})
        curr += 1
        rate_db_ts2 = self.db_manager.set_rates('USD', {'EUR': curr})
        rates = self.db_manager.get_rates("USD", 2, target_currency="EUR")
        ts1, rate1 = rates[0]
        ts2, rate2 = rates[1]

        assert (rate_db_ts1 == ts1 and rate_db_ts2 == ts2), "Failed read sorted test case! " \
                                                            "Sorting is not right!"
        # delete rates that are saved for the test
        assert self.db_manager.delete_rate(rate_db_ts1, rate_db_ts2)
