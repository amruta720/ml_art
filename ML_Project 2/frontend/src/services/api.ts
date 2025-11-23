/**
 * API client for communicating with the backend
 */
import {
  ImageModeRequest,
  ImageModeResponse,
  StoryModeRequest,
  StoryModeResponse,
  RevisionRequest,
  HealthResponse,
  EditTextSegmentRequest,
  EditTextSegmentResponse,
  DownloadStorybookRequest,
  ThreePhaseStoryRequest,
  ThreePhaseStoryResponse,
  StoryAsset,
  AssetUsage,
  UploadAssetResponse,
} from '../types';

const API_BASE_URL = '/api';

class ApiClient {
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    const config: RequestInit = {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    };

    const response = await fetch(url, config);

    if (!response.ok) {
      const error = await response.json().catch(() => ({
        detail: response.statusText,
      }));
      throw new Error(error.detail || 'API request failed');
    }

    return response.json();
  }

  async checkHealth(): Promise<HealthResponse> {
    return this.request<HealthResponse>('/health');
  }

  async generateImage(
    request: ImageModeRequest
  ): Promise<ImageModeResponse> {
    return this.request<ImageModeResponse>('/image-mode', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async generateStorybook(
    request: StoryModeRequest
  ): Promise<StoryModeResponse> {
    return this.request<StoryModeResponse>('/story-mode', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async reviseImage(
    request: RevisionRequest
  ): Promise<ImageModeResponse> {
    return this.request<ImageModeResponse>('/revise', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async editTextSegment(
    request: EditTextSegmentRequest
  ): Promise<EditTextSegmentResponse> {
    return this.request<EditTextSegmentResponse>('/edit_text_segment', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  downloadImage(filename: string, format: string = 'png'): string {
    // Extract just the filename without path
    const baseFilename = filename.split('/').pop() || filename;
    return `${API_BASE_URL}/download_image/${baseFilename}?format=${format}`;
  }

  async downloadStorybook(request: DownloadStorybookRequest): Promise<void> {
    const url = `${API_BASE_URL}/download_storybook`;
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({
        detail: response.statusText,
      }));
      throw new Error(error.detail || 'PDF download failed');
    }

    // Trigger download
    const blob = await response.blob();
    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = `${request.story_title.replace(/[^a-z0-9]/gi, '_')}.pdf`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(downloadUrl);
  }

  async generateStorybook3Phase(
    request: ThreePhaseStoryRequest
  ): Promise<ThreePhaseStoryResponse> {
    return this.request<ThreePhaseStoryResponse>('/generate-storybook-3phase', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async uploadAsset(
    file: File,
    usage: AssetUsage = AssetUsage.STYLE,
    description?: string
  ): Promise<UploadAssetResponse> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('usage', usage);
    if (description) {
      formData.append('description', description);
    }

    const response = await fetch(`${API_BASE_URL}/upload-asset`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({
        detail: response.statusText,
      }));
      throw new Error(error.detail || 'Asset upload failed');
    }

    return response.json();
  }

  async listAssets(): Promise<StoryAsset[]> {
    return this.request<StoryAsset[]>('/assets');
  }

  async deleteAsset(assetId: string): Promise<{ message: string }> {
    const response = await fetch(`${API_BASE_URL}/assets/${assetId}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({
        detail: response.statusText,
      }));
      throw new Error(error.detail || 'Asset deletion failed');
    }

    return response.json();
  }
}

export const apiClient = new ApiClient();
