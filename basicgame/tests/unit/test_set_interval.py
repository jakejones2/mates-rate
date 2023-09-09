from basicgame.set_interval import setIntervalAsync
from basicgame.tests.unit.base import TripleTest
import asyncio


class TestSetIntervalAsync(TripleTest):
    """
    Instances of class should be able to execute a function
    periodically in a new asyncio task.
    """

    async def test_class_executes_the_given_function_periodically(self):
        counter = {"count": 0}

        async def testfunc():
            counter["count"] += 1

        test_interval = setIntervalAsync(testfunc, 0, 0.01, 2)
        await test_interval.start()
        await asyncio.sleep(0.01)
        self.assertEqual(counter["count"], 1)
        await asyncio.sleep(0.01)
        self.assertEqual(counter["count"], 2)
        await test_interval.stop()

    async def test_default_period_is_two_seconds(self):
        counter = {"count": 0}

        async def testfunc():
            counter["count"] += 1

        test_interval = setIntervalAsync(testfunc, 0)
        await test_interval.start()
        await asyncio.sleep(2)
        self.assertEqual(counter["count"], 1)
        await test_interval.stop()

    async def test_default_maximum_executions_is_thirty(self):
        counter = {"count": 0}

        async def testfunc():
            counter["count"] += 1

        test_interval = setIntervalAsync(testfunc, 0, 0.001)
        await test_interval.start()
        await asyncio.sleep(0.04)
        await test_interval.stop()
        self.assertEqual(counter["count"], 30)

    async def test_maximum_executions_is_settable(self):
        counter = {"count": 0}

        async def testfunc():
            counter["count"] += 1

        test_interval = setIntervalAsync(testfunc, 0, 0.001, 23)
        await test_interval.start()
        await asyncio.sleep(0.04)
        await test_interval.stop()
        self.assertEqual(counter["count"], 23)

    async def test_period_can_be_stopped(self):
        counter = {"count": 0}

        async def testfunc():
            counter["count"] += 1

        test_interval = setIntervalAsync(testfunc, 0, 0.01)
        await test_interval.start()
        await asyncio.sleep(0.04)
        await test_interval.stop()
        self.assertEqual(counter["count"], 4)

    async def test_second_argument_stores_round_called_on(self):
        counter = {"count": 0}

        async def testfunc():
            counter["count"] += 1

        test_interval = setIntervalAsync(testfunc, "pancake", 0.1)
        self.assertEqual(test_interval.progress, "pancake")

    async def test_instances_of_set_interval_behave_concurrently(self):
        counter = {"count": 0}

        async def testfunc():
            counter["count"] += 1

        test_interval = setIntervalAsync(testfunc, 0, 0.01, 2)
        counter2 = {"count": 0}

        async def testfunc2():
            counter2["count"] += 1

        test_interval2 = setIntervalAsync(testfunc2, 0, 0.01, 2)
        await test_interval.start()
        await test_interval2.start()
        await asyncio.sleep(0.01)
        self.assertEqual(counter["count"], 1)
        self.assertEqual(counter2["count"], 1)
        await asyncio.sleep(0.01)
        self.assertEqual(counter["count"], 2)
        self.assertEqual(counter2["count"], 2)
        await test_interval.stop()
