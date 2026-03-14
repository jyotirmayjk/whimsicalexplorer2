import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import HomeScreen from '../screens/Home/HomeScreen';
import DiscoveriesScreen from '../screens/Discoveries/DiscoveriesScreen';
import ActivityScreen from '../screens/Activity/ActivityScreen';

export type MainTabParamList = {
  Home: undefined;
  Discoveries: undefined;
  Activity: undefined;
};

const Tab = createBottomTabNavigator<MainTabParamList>();

const TabNavigator = () => {
  return (
    <Tab.Navigator screenOptions={{ headerShown: false }}>
      <Tab.Screen name="Home" component={HomeScreen} />
      <Tab.Screen name="Discoveries" component={DiscoveriesScreen} />
      <Tab.Screen name="Activity" component={ActivityScreen} />
    </Tab.Navigator>
  );
};

export default TabNavigator;
