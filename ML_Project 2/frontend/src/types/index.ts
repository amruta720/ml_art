/**
 * TypeScript types matching backend schemas
 */

export enum ImageStyle {
  REALISTIC = 'realistic',
  ARTISTIC = 'artistic',
  ANIME = 'anime',
  FANTASY = 'fantasy',
  SCIFI = 'sci-fi',
  WATERCOLOR = 'watercolor',
  OIL_PAINTING = 'oil painting',
  DIGITAL_ART = 'digital art',
}

export interface ImageModeRequest {
  prompt: string;
  style?: ImageStyle;
  enhance_prompt?: boolean;
  asset_ids?: string[];
}

export interface ImageModeResponse {
  image_url: string;
  original_prompt: string;
  enhanced_prompt: string;
  style_applied?: string;
  generation_time: number;
}

export interface DialogueLine {
  speaker: string;
  text: string;
}

export interface StoryPanel {
  panel_number: number;
  title: string;
  narration: string;
  dialogues: DialogueLine[];
  scene_description: string;
  image_prompt: string;
  image_url?: string;
}

export interface StoryModeRequest {
  story_idea: string;
  num_panels: number;
  style?: ImageStyle;
  asset_ids?: string[];
}

export interface StoryModeResponse {
  story_title: string;
  panels: StoryPanel[];
  style_applied?: string;
  total_generation_time: number;
}

export interface RevisionRequest {
  original_prompt: string;
  feedback: string;
  style?: ImageStyle;
}

export interface HealthResponse {
  status: string;
  models_loaded: boolean;
}

export interface EditTextSegmentRequest {
  original_text: string;
  instruction: string;
  context?: string;
}

export interface EditTextSegmentResponse {
  edited_text: string;
}

export interface DownloadStorybookRequest {
  story_title: string;
  panels: StoryPanel[];
}

// ============================================================================
// THREE-PHASE STORYBOOK PIPELINE TYPES
// ============================================================================

export interface StoryPage {
  page_number: number;
  title: string;
  outline: string;
  scene_description: string;
  narration: string;
  dialogues: DialogueLine[];
  art_prompt?: string;
  negative_prompt?: string;
  image_url?: string;
}

export interface StoryMeta {
  title: string;
  logline: string;
  age_range: string;
  style_preset: string;
  characters: string[];
}

export interface StoryBook {
  id: string;
  meta: StoryMeta;
  pages: StoryPage[];
}

export interface ThreePhaseStoryRequest {
  story_idea: string;
  num_pages: number;
  age_range?: string;
  style?: ImageStyle;
  asset_ids?: string[];
}

export interface ThreePhaseStoryResponse {
  storybook: StoryBook;
  total_generation_time: number;
  phase_times: Record<string, number>;
}

// ============================================================================
// ASSET SYSTEM TYPES
// ============================================================================

export enum AssetUsage {
  STYLE = 'style',
  CHARACTER = 'character',
  STORY_SOURCE = 'story_source',
  BASE_IMAGE = 'base_image',
}

export interface StoryAsset {
  id: string;
  url: string;
  filename: string;
  mime_type: string;
  usage: AssetUsage;
  description?: string;
}

export interface UploadAssetResponse {
  asset: StoryAsset;
  message: string;
}
