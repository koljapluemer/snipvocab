export interface Snippet {
  id: number;
  text: string;
}

export function getVideoSnippets(videoId: string): Promise<Snippet[]>; 