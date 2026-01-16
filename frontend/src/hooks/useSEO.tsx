// src/hooks/useSEO.ts

import { Helmet } from 'react-helmet-async';

interface SEOConfig {
  title: string;
  description: string;
  image?: string;
  url?: string;
}

/**
 * Custom hook for managing SEO meta tags using react-helmet-async
 *
 * @param config - SEO configuration object
 * @param config.title - Page title
 * @param config.description - Page description
 * @param config.image - Open Graph image URL (optional)
 * @param config.url - Canonical URL (optional)
 *
 * @returns Helmet component with meta tags
 *
 * @example
 * ```tsx
 * const seoConfig = {
 *   title: 'ContraVento - Pedalear para Conectar',
 *   description: 'Una plataforma para ciclistas...',
 *   image: '/assets/images/landing/hero.jpg',
 *   url: 'https://contravento.com',
 * };
 *
 * return (
 *   <>
 *     {useSEO(seoConfig)}
 *     <div>Page content...</div>
 *   </>
 * );
 * ```
 */
export const useSEO = ({ title, description, image, url }: SEOConfig) => {
  return (
    <Helmet>
      {/* Basic meta tags */}
      <title>{title}</title>
      <meta name="description" content={description} />

      {/* Open Graph meta tags */}
      <meta property="og:title" content={title} />
      <meta property="og:description" content={description} />
      {image && <meta property="og:image" content={image} />}
      {url && <meta property="og:url" content={url} />}
      <meta property="og:type" content="website" />

      {/* Twitter Card meta tags */}
      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:title" content={title} />
      <meta name="twitter:description" content={description} />
      {image && <meta name="twitter:image" content={image} />}
    </Helmet>
  );
};
