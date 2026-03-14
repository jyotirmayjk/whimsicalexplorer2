import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import TabNavigator from './TabNavigator';
import OnboardingNavigator from './OnboardingNavigator';
import SettingsScreen from '../screens/Settings/SettingsScreen';

export type RootStackParamList = {
  Onboarding: undefined;
  MainTabs: undefined;
  Settings: undefined;
};

const Stack = createNativeStackNavigator<RootStackParamList>();

const RootNavigator = () => {
  return (
    <NavigationContainer>
      <Stack.Navigator screenOptions={{ headerShown: false }} initialRouteName="Onboarding">
        <Stack.Screen name="Onboarding" component={OnboardingNavigator} />
        <Stack.Screen name="MainTabs" component={TabNavigator} />
        <Stack.Screen name="Settings" component={SettingsScreen} />
      </Stack.Navigator>
    </NavigationContainer>
  );
};

export default RootNavigator;
