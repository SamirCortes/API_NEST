import { ApiResponse } from '../interfaces/api-response.interface';

export class ApiResponseDto<T = unknown> implements ApiResponse<T> {
  status: boolean;
  message: string;
  data?: T;

  private constructor(status: boolean, message: string, data?: T) {
    this.status = status;
    this.message = message;
    if (data !== undefined) {
      this.data = data;
    }
  }

  static success<T>(message: string, data?: T): ApiResponseDto<T> {
    return new ApiResponseDto(true, message, data);
  }

  static fail(message: string): ApiResponseDto {
    return new ApiResponseDto(false, message);
  }
}
