import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';

import WelcomeScreen from '../screens/Onboarding/WelcomeScreen';
import VoiceStyleScreen from '../screens/Onboarding/VoiceStyleScreen';
import CategoryScreen from '../screens/Onboarding/CategoryScreen';
import DefaultModeScreen from '../screens/Onboarding/DefaultModeScreen';

export type OnboardingParamList = {
  Welcome: undefined;
  VoiceStyle: undefined;
  CategorySelection: undefined;
  DefaultMode: undefined;
  MainTabs: undefined; // Escape hatch
};

const Stack = createNativeStackNavigator<OnboardingParamList>();

const OnboardingNavigator = () => {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      <Stack.Screen name="Welcome" component={WelcomeScreen} />
      <Stack.Screen name="VoiceStyle" component={VoiceStyleScreen} />
      <Stack.Screen name="CategorySelection" component={CategoryScreen} />
      <Stack.Screen name="DefaultMode" component={DefaultModeScreen} />
    </Stack.Navigator>
  );
};

export default OnboardingNavigator;
