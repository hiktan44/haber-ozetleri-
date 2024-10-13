import React, { useState, useEffect } from 'react';
import { View, Text, FlatList, StyleSheet } from 'react-native';
import * as rssParser from 'react-native-rss-parser';
import axios from 'axios';

export default function FeedScreen({ route }) {
  const { feedUrl } = route.params;
  const [feedItems, setFeedItems] = useState([]);

  useEffect(() => {
    fetchFeed();
  }, []);

  const fetchFeed = async () => {
    try {
      const response = await axios.get(feedUrl);
      const parsedFeed = await rssParser.parse(response.data);
      setFeedItems(parsedFeed.items);
    } catch (error) {
      console.error('Error fetching feed:', error);
    }
  };

  return (
    <View style={styles.container}>
      <FlatList
        data={feedItems}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => (
          <View style={styles.feedItem}>
            <Text style={styles.title}>{item.title}</Text>
            <Text style={styles.description}>{item.description}</Text>
          </View>
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
  },
  feedItem: {
    marginBottom: 20,
  },
  title: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 5,
  },
  description: {
    fontSize: 14,
  },
});
