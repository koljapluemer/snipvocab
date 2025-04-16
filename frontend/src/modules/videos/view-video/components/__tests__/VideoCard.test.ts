// *per module test example*

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { mount } from '@vue/test-utils';
import VideoCard from '../VideoCard.vue';
import { getVideoSnippets } from '@/modules/backend-communication/api';

// Mock the API call
vi.mock('@/modules/backend-communication/api', () => ({
  getVideoSnippets: vi.fn()
}));

describe('VideoCard', () => {
  const mockVideoId = 'test123';
  const mockSnippets = [
    { id: 1, text: 'Test snippet 1' },
    { id: 2, text: 'Test snippet 2' }
  ];

  beforeEach(() => {
    // Reset all mocks before each test
    vi.clearAllMocks();
    // Mock the API response
    (getVideoSnippets as any).mockResolvedValue(mockSnippets);
  });

  it('renders correctly and displays snippet count', async () => {
    const wrapper = mount(VideoCard, {
      props: {
        videoId: mockVideoId
      }
    });

    // Initially, the snippet count should be 0
    expect(wrapper.text()).toContain('0 snippets');

    // Wait for the component to finish loading and API call to complete
    await wrapper.vm.$nextTick();
    await new Promise(resolve => setTimeout(resolve, 0));

    // After API call completes, the snippet count should be updated
    expect(wrapper.text()).toContain(`${mockSnippets.length} snippets`);

    // Check if the video ID is used in the image source
    expect(wrapper.find('img').attributes('src')).toContain(mockVideoId);

    // Check if the "View Details" button is present and has correct route
    const viewDetailsButton = wrapper.find('a.btn-primary');
    expect(viewDetailsButton.exists()).toBe(true);
    expect(viewDetailsButton.attributes('href')).toContain(mockVideoId);
  });

  it('handles API error gracefully', async () => {
    // Mock API error
    (getVideoSnippets as any).mockRejectedValue(new Error('API Error'));

    const wrapper = mount(VideoCard, {
      props: {
        videoId: mockVideoId
      }
    });

    // Initially, the snippet count should be 0
    expect(wrapper.text()).toContain('0 snippets');

    // Wait for the component to finish loading and API call to complete
    await wrapper.vm.$nextTick();
    await new Promise(resolve => setTimeout(resolve, 0));

    // After API error, the snippet count should remain 0
    expect(wrapper.text()).toContain('0 snippets');
  });
}); 