export type {
  Address,
  Coordinates,
  DeclaredValue,
  DeliveryWindow,
  DimensionUnit,
  Dimensions,
  LocalizedDescription,
  Location,
  Operator,
  Piece,
  Shipment,
  TrackingEvent,
  Transport,
  TransportMode,
  UlscCategory,
  UlscCode,
  Weight,
  WeightUnit,
} from "./types.js";

export { CATEGORY, ULSC_CODES, categoryOf, isValidUlscCode } from "./ulsc.js";
export { event, shipment } from "./normalize.js";
