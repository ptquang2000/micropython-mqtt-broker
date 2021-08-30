from server import Topic
import unittest

class TestTopic(unittest.TestCase):

    def setUp(self):
        self.result = {b'topic0': 
                                        {b'topic1': 
                                            {b'topic2': b'msg'}
                                        }
                                    }
        self.result2 = {b'topic3': b'msg',
                                        b'topic0': 
                                            {b'topic1': 
                                                {b'topic2': b'msg'}
                                            }
                                        }
        self.result3 = {b'topic0': 
                                            {b'topic1': 
                                                {b'topic2': b'msg',
                                                  b'topic3': b'msg'
                                                }
                                            }
                                        }

    def test_empty_topic(self):
        topic = Topic()
        topic[b'topic0/topic1/topic2'] = b'msg'
        self.assertEqual(topic, self.result)

    def test_existing_sub(self):
        topic_storage = {b'topic0': 
                                            {b'topic1': 
                                                {b'topic2': 'not msg'}
                                            }
                                        }
        topic = Topic(topic_storage)
        topic[b'topic0/topic1/topic2'] = b'msg'
        self.assertEqual(topic, self.result)

        topic_storage = {b'topic0': 
                                            {b'topic1': 
                                                {b'topic2': 
                                                    {b'topic3': b'msg'}}
                                            }
                                        }
        topic = Topic(topic_storage)
        topic[b'topic0/topic1/topic2'] = b'msg'
        self.assertEqual(topic, self.result)

    def test_none_existing_topic(self):
        topic_storage = {b'topic0': 
                                            {b'topic1': b'msg'}
                                        }
        topic = Topic(topic_storage)
        topic[b'topic0/topic1/topic2'] = b'msg'
        self.assertEqual(topic, self.result)

        topic_storage = {b'topic0': b'msg'}
        topic = Topic(topic_storage)
        topic[b'topic0/topic1/topic2'] = b'msg'
        self.assertEqual(topic, self.result)

        topic_storage = {b'topic0': b'msg'}
        topic = Topic(topic_storage)
        topic[b'topic0/topic1/topic2'] = b'msg'
        self.assertEqual(topic, self.result)

        topic_storage = {b'topic3': b'msg'} 
        topic = Topic(topic_storage)
        topic[b'topic0/topic1/topic2'] = b'msg'
        self.assertEqual(topic, self.result2)

        topic_storage = {b'topic0': 
                                            {b'topic1': 
                                                {b'topic3': b'msg'}
                                            }
                                        }
        topic = Topic(topic_storage)
        topic[b'topic0/topic1/topic2'] = b'msg'
        self.assertEqual(topic, self.result3)

    def test_get_appmsg(self):
        topic = Topic()
        self.assertEqual(topic[b'topic0'], None)

        topic_storage = {b'topic0':b'msg'}
        topic = Topic(topic_storage)
        self.assertEqual(topic[b'topic0'], b'msg')

        topic_storage = {b'topic0': 
                                            {b'topic1':b'msg'}
                                        }
        topic = Topic(topic_storage)
        self.assertEqual(topic[b'topic0/topic1'], b'msg')

        topic_storage = {b'topic0': 
                                            {b'topic1': 
                                                {b'topic2': b'msg'}
                                            }
                                        }
        topic = Topic(topic_storage)
        self.assertEqual(topic[b'topic0/topic1/topic2'], b'msg')

    def test_get_appmsg_sub(self):
        topic_storage = {b'topic0': 
                                            {b'topic1': {
                                                    b'topic2': b'msg',
                                                    b'topic3': b'msg'
                                                }
                                            }
                                        }
        topic = Topic(topic_storage)
        self.assertEqual(topic[b'topic0'], None)
        self.assertEqual(topic[b'topic0/topic1'], None)
        self.assertEqual(topic[b'topic0/topic1/topic4'], None)
        self.assertEqual(topic[b'topic0/topic1/topic2'], b'msg')
        self.assertEqual(topic[b'topic0/topic1/topic3'], b'msg')

if __name__ == '__main__':
    unittest.main()
