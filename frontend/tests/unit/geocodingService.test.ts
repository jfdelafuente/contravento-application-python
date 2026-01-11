/**
 * Unit tests for geocodingService
 * Feature: 010-reverse-geocoding
 * Tests: T010, T011
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import axios from 'axios';
import MockAdapter from 'axios-mock-adapter';
import {
  reverseGeocode,
  extractLocationName,
} from '../../src/services/geocodingService';
import type { GeocodingResponse } from '../../src/types/geocoding';

describe('geocodingService', () => {
  let mockAxios: MockAdapter;

  beforeEach(() => {
    mockAxios = new MockAdapter(axios);
  });

  afterEach(() => {
    mockAxios.restore();
  });

  describe('reverseGeocode', () => {
    const validLat = 40.416775;
    const validLng = -3.70379;

    const mockSuccessResponse: GeocodingResponse = {
      place_id: 123456789,
      licence: 'Data © OpenStreetMap contributors, ODbL 1.0',
      osm_type: 'way',
      osm_id: 987654321,
      lat: '40.416775',
      lon: '-3.703790',
      display_name: 'Parque del Retiro, Retiro, Madrid, Comunidad de Madrid, 28009, España',
      address: {
        leisure: 'Parque del Retiro',
        suburb: 'Retiro',
        city: 'Madrid',
        state: 'Comunidad de Madrid',
        postcode: '28009',
        country: 'España',
        country_code: 'es',
      },
      boundingbox: ['40.4089508', '40.4226627', '-3.6914111', '-3.6753464'],
    };

    it('should successfully reverse geocode valid coordinates', async () => {
      // Arrange
      mockAxios.onGet(/nominatim.*reverse/).reply(200, mockSuccessResponse);

      // Act
      const result = await reverseGeocode(validLat, validLng);

      // Assert
      expect(result).toEqual(mockSuccessResponse);
      expect(result.display_name).toBe('Parque del Retiro, Retiro, Madrid, Comunidad de Madrid, 28009, España');
      expect(result.address.leisure).toBe('Parque del Retiro');
    });

    it('should send correct query parameters to Nominatim API', async () => {
      // Arrange
      mockAxios.onGet(/nominatim.*reverse/).reply((config) => {
        expect(config.params.lat).toBe(validLat);
        expect(config.params.lon).toBe(validLng);
        expect(config.params.format).toBe('json');
        expect(config.params['accept-language']).toBe('es');
        expect(config.params.addressdetails).toBe(1);
        expect(config.params.zoom).toBe(18);
        return [200, mockSuccessResponse];
      });

      // Act
      await reverseGeocode(validLat, validLng);

      // Assert - expectations in reply callback
    });

    it('should send User-Agent header', async () => {
      // Arrange
      mockAxios.onGet(/nominatim.*reverse/).reply((config) => {
        expect(config.headers?.['User-Agent']).toBe('ContraVento/1.0 (contact@contravento.com)');
        return [200, mockSuccessResponse];
      });

      // Act
      await reverseGeocode(validLat, validLng);

      // Assert - expectations in reply callback
    });

    it('should throw error for invalid latitude (< -90)', async () => {
      // Arrange
      const invalidLat = -100;

      // Act & Assert
      await expect(reverseGeocode(invalidLat, validLng)).rejects.toThrow(
        'Latitud inválida: debe estar entre -90 y 90 grados'
      );
    });

    it('should throw error for invalid latitude (> 90)', async () => {
      // Arrange
      const invalidLat = 100;

      // Act & Assert
      await expect(reverseGeocode(invalidLat, validLng)).rejects.toThrow(
        'Latitud inválida: debe estar entre -90 y 90 grados'
      );
    });

    it('should throw error for invalid longitude (< -180)', async () => {
      // Arrange
      const invalidLng = -200;

      // Act & Assert
      await expect(reverseGeocode(validLat, invalidLng)).rejects.toThrow(
        'Longitud inválida: debe estar entre -180 y 180 grados'
      );
    });

    it('should throw error for invalid longitude (> 180)', async () => {
      // Arrange
      const invalidLng = 200;

      // Act & Assert
      await expect(reverseGeocode(validLat, invalidLng)).rejects.toThrow(
        'Longitud inválida: debe estar entre -180 y 180 grados'
      );
    });

    it('should throw error when Nominatim returns error response', async () => {
      // Arrange
      mockAxios.onGet(/nominatim.*reverse/).reply(200, {
        error: 'Unable to geocode',
      });

      // Act & Assert
      await expect(reverseGeocode(validLat, validLng)).rejects.toThrow(
        'No se pudo obtener el nombre del lugar: Unable to geocode'
      );
    });

    it('should throw Spanish error for rate limit (429)', async () => {
      // Arrange
      mockAxios.onGet(/nominatim.*reverse/).reply(429, 'Too many requests');

      // Act & Assert
      await expect(reverseGeocode(validLat, validLng)).rejects.toThrow(
        'Demasiadas solicitudes. Por favor, espera un momento e intenta de nuevo.'
      );
    });

    it('should throw Spanish error for network timeout', async () => {
      // Arrange
      mockAxios.onGet(/nominatim.*reverse/).timeout();

      // Act & Assert
      await expect(reverseGeocode(validLat, validLng)).rejects.toThrow(
        'El servidor de mapas no responde. Verifica tu conexión a internet.'
      );
    });

    it('should throw Spanish error for generic network error', async () => {
      // Arrange
      mockAxios.onGet(/nominatim.*reverse/).networkError();

      // Act & Assert
      await expect(reverseGeocode(validLat, validLng)).rejects.toThrow(
        'No se pudo conectar con el servicio de mapas. Intenta nuevamente.'
      );
    });
  });

  describe('extractLocationName', () => {
    it('should prioritize leisure field (park, garden)', () => {
      // Arrange
      const response: GeocodingResponse = {
        place_id: 1,
        licence: '',
        osm_type: 'way',
        osm_id: 1,
        lat: '40.4',
        lon: '-3.7',
        display_name: 'Full address',
        address: {
          leisure: 'Parque del Retiro',
          amenity: 'Restaurant',
          road: 'Calle Mayor',
          city: 'Madrid',
        },
        boundingbox: ['0', '0', '0', '0'],
      };

      // Act
      const name = extractLocationName(response);

      // Assert
      expect(name).toBe('Parque del Retiro');
    });

    it('should use amenity if leisure not available', () => {
      // Arrange
      const response: GeocodingResponse = {
        place_id: 1,
        licence: '',
        osm_type: 'way',
        osm_id: 1,
        lat: '40.4',
        lon: '-3.7',
        display_name: 'Full address',
        address: {
          amenity: 'Hospital Gregorio Marañón',
          road: 'Calle Mayor',
          city: 'Madrid',
        },
        boundingbox: ['0', '0', '0', '0'],
      };

      // Act
      const name = extractLocationName(response);

      // Assert
      expect(name).toBe('Hospital Gregorio Marañón');
    });

    it('should use tourism if leisure and amenity not available', () => {
      // Arrange
      const response: GeocodingResponse = {
        place_id: 1,
        licence: '',
        osm_type: 'way',
        osm_id: 1,
        lat: '40.4',
        lon: '-3.7',
        display_name: 'Full address',
        address: {
          tourism: 'Museo del Prado',
          road: 'Calle Mayor',
          city: 'Madrid',
        },
        boundingbox: ['0', '0', '0', '0'],
      };

      // Act
      const name = extractLocationName(response);

      // Assert
      expect(name).toBe('Museo del Prado');
    });

    it('should use shop if higher priorities not available', () => {
      // Arrange
      const response: GeocodingResponse = {
        place_id: 1,
        licence: '',
        osm_type: 'way',
        osm_id: 1,
        lat: '40.4',
        lon: '-3.7',
        display_name: 'Full address',
        address: {
          shop: 'El Corte Inglés',
          road: 'Calle Mayor',
          city: 'Madrid',
        },
        boundingbox: ['0', '0', '0', '0'],
      };

      // Act
      const name = extractLocationName(response);

      // Assert
      expect(name).toBe('El Corte Inglés');
    });

    it('should use road if no POI fields available', () => {
      // Arrange
      const response: GeocodingResponse = {
        place_id: 1,
        licence: '',
        osm_type: 'way',
        osm_id: 1,
        lat: '40.4',
        lon: '-3.7',
        display_name: 'Full address',
        address: {
          road: 'Calle de Alcalá',
          city: 'Madrid',
        },
        boundingbox: ['0', '0', '0', '0'],
      };

      // Act
      const name = extractLocationName(response);

      // Assert
      expect(name).toBe('Calle de Alcalá');
    });

    it('should use city if no road available', () => {
      // Arrange
      const response: GeocodingResponse = {
        place_id: 1,
        licence: '',
        osm_type: 'way',
        osm_id: 1,
        lat: '40.4',
        lon: '-3.7',
        display_name: 'Full address',
        address: {
          city: 'Madrid',
        },
        boundingbox: ['0', '0', '0', '0'],
      };

      // Act
      const name = extractLocationName(response);

      // Assert
      expect(name).toBe('Madrid');
    });

    it('should use town if city not available', () => {
      // Arrange
      const response: GeocodingResponse = {
        place_id: 1,
        licence: '',
        osm_type: 'way',
        osm_id: 1,
        lat: '40.4',
        lon: '-3.7',
        display_name: 'Full address',
        address: {
          town: 'Alcalá de Henares',
        },
        boundingbox: ['0', '0', '0', '0'],
      };

      // Act
      const name = extractLocationName(response);

      // Assert
      expect(name).toBe('Alcalá de Henares');
    });

    it('should use village if city and town not available', () => {
      // Arrange
      const response: GeocodingResponse = {
        place_id: 1,
        licence: '',
        osm_type: 'way',
        osm_id: 1,
        lat: '40.4',
        lon: '-3.7',
        display_name: 'Full address',
        address: {
          village: 'Puebla de la Sierra',
        },
        boundingbox: ['0', '0', '0', '0'],
      };

      // Act
      const name = extractLocationName(response);

      // Assert
      expect(name).toBe('Puebla de la Sierra');
    });

    it('should use display_name if all address fields are empty', () => {
      // Arrange
      const response: GeocodingResponse = {
        place_id: 1,
        licence: '',
        osm_type: 'way',
        osm_id: 1,
        lat: '40.4',
        lon: '-3.7',
        display_name: 'Some remote location in Spain',
        address: {},
        boundingbox: ['0', '0', '0', '0'],
      };

      // Act
      const name = extractLocationName(response);

      // Assert
      expect(name).toBe('Some remote location in Spain');
    });

    it('should truncate display_name if longer than 50 characters', () => {
      // Arrange
      const longAddress = 'This is a very long address that exceeds fifty characters in total length';
      const response: GeocodingResponse = {
        place_id: 1,
        licence: '',
        osm_type: 'way',
        osm_id: 1,
        lat: '40.4',
        lon: '-3.7',
        display_name: longAddress,
        address: {},
        boundingbox: ['0', '0', '0', '0'],
      };

      // Act
      const name = extractLocationName(response);

      // Assert
      expect(name).toBe(longAddress.substring(0, 50) + '...');
      expect(name.length).toBe(53); // 50 + '...'
    });

    it('should return fallback if display_name and address are empty', () => {
      // Arrange
      const response: GeocodingResponse = {
        place_id: 1,
        licence: '',
        osm_type: 'way',
        osm_id: 1,
        lat: '40.4',
        lon: '-3.7',
        display_name: '',
        address: {},
        boundingbox: ['0', '0', '0', '0'],
      };

      // Act
      const name = extractLocationName(response);

      // Assert
      expect(name).toBe('Ubicación sin nombre');
    });
  });
});
