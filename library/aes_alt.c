/*
 *  Implementation reference of AES alternative function
 *
 *  Copyright The Mbed TLS Contributors
 *  SPDX-License-Identifier: Apache-2.0
 *
 *  Licensed under the Apache License, Version 2.0 (the "License"); you may
 *  not use this file except in compliance with the License.
 *  You may obtain a copy of the License at
 *
 *  http://www.apache.org/licenses/LICENSE-2.0
 *
 *  Unless required by applicable law or agreed to in writing, software
 *  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 *  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *  See the License for the specific language governing permissions and
 *  limitations under the License.
 */

#include "common.h"

#if defined(MBEDTLS_AES_C)

#include "mbedtls/aes.h"
#include "mbedtls/error.h"

#if defined(MBEDTLS_AES_DECRYPT_ALT)
int mbedtls_internal_aes_decrypt(mbedtls_aes_context *ctx,
                                 const unsigned char input[16],
                                 unsigned char output[16])
{
    (void) ctx;
    (void) input;
    (void) output;

    return MBEDTLS_ERR_PLATFORM_FEATURE_UNSUPPORTED;
}
#endif /* MBEDTLS_AES_DECRYPT_ALT */

#endif /* MBEDTLS_AES_C */
