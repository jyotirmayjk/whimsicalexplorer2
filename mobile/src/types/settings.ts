export interface ChildSettings {
  voiceStyle: 'friendly_cartoon' | 'story_narrator';
  defaultMode: 'story' | 'learn' | 'explorer';
  allowedCategories: ('animals' | 'vehicles' | 'toys' | 'household_objects')[];
}
