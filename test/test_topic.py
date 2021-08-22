from server import Topic
import unittest

class TestTopic(unittest.TestCase):

  def setUp(self):
    self.result = {'topic0': 
                    {'topic1': 
                      {'topic2': 'msg'}
                    }
                  }
    self.result2 = {'topic3': 'msg',
                    'topic0': 
                      {'topic1': 
                        {'topic2': 'msg'}
                      }
                    }
    self.result3 = {'topic0': 
                      {'topic1': 
                        {'topic2': 'msg',
                         'topic3': 'msg'
                        }
                      }
                    }

  def test_empty_topic(self):
    topic_storage = {}
    topic = Topic(topic_storage)
    topic['topic0/topic1/topic2'] = 'msg'
    self.assertEqual(topic_storage, self.result)

  def test_existing_sub(self):
    topic_storage = {'topic0': 
                      {'topic1': 
                        {'topic2': 'not msg'}
                      }
                    }
    topic = Topic(topic_storage)
    topic['topic0/topic1/topic2'] = 'msg'
    self.assertEqual(topic_storage, self.result)

    topic_storage = {'topic0': 
                      {'topic1': 
                        {'topic2': 
                          {'topic3': 'msg'}}
                      }
                    }
    topic = Topic(topic_storage)
    topic['topic0/topic1/topic2'] = 'msg'
    self.assertEqual(topic_storage, self.result)

  def test_none_existing_topic(self):
    topic_storage = {'topic0': 
                      {'topic1': 'msg'}
                    }
    topic = Topic(topic_storage)
    topic['topic0/topic1/topic2'] = 'msg'
    self.assertEqual(topic_storage, self.result)

    topic_storage = {'topic0': 'msg'}
    topic = Topic(topic_storage)
    topic['topic0/topic1/topic2'] = 'msg'
    self.assertEqual(topic_storage, self.result)

    topic_storage = {'topic0': 'msg'}
    topic = Topic(topic_storage)
    topic['topic0/topic1/topic2'] = 'msg'
    self.assertEqual(topic_storage, self.result)

    topic_storage = {'topic3': 'msg'} 
    topic = Topic(topic_storage)
    topic['topic0/topic1/topic2'] = 'msg'
    self.assertEqual(topic_storage, self.result2)

    topic_storage = {'topic0': 
                      {'topic1': 
                        {'topic3': 'msg'}
                      }
                    }
    topic = Topic(topic_storage)
    topic['topic0/topic1/topic2'] = 'msg'
    self.assertEqual(topic_storage, self.result3)

if __name__ == '__main__':
  unittest.main()
