import React, { useState } from 'react';
import { View, Text, TextInput, Button, FlatList, StyleSheet } from 'react-native';

export default function HomeScreen({ navigation }) {
  const [feeds, setFeeds] = useState([]);
  const [newFeed, setNewFeed] = useState('');

  const addFeed = () => {
    if (newFeed) {
      setFeeds([...feeds, newFeed]);
      setNewFeed('');
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>RSS Feed Summary Generator</Text>
      <View style={styles.inputContainer}>
        <TextInput
          style={styles.input}
          value={newFeed}
          onChangeText={setNewFeed}
          placeholder="Enter RSS feed URL"
        />
        <Button title="Add Feed" onPress={addFeed} />
      </View>
      <FlatList
        data={feeds}
        keyExtractor={(item, index) => index.toString()}
        renderItem={({ item }) => (
          <View style={styles.feedItem}>
            <Text>{item}</Text>
            <Button
              title="View"
              onPress={() => navigation.navigate('Feed', { feedUrl: item })}
            />
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
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 20,
  },
  inputContainer: {
    flexDirection: 'row',
    marginBottom: 20,
  },
  input: {
    flex: 1,
    marginRight: 10,
    borderWidth: 1,
    borderColor: '#ccc',
    padding: 10,
  },
  feedItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#ccc',
  },
});
