#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <curl/curl.h>
#include <zlib.h>

#define CHUNK_SIZE 16384

static size_t write_data(void *ptr, size_t size, size_t nmemb, void *stream) {
    size_t realsize = size * nmemb;
    return fwrite(ptr, 1, realsize, (FILE *)stream);
}

unsigned char *get_little_endian_data(const char *url, size_t *data_size) {
    CURL *curl;
    FILE *fp;
    CURLcode res;
    unsigned char *data = NULL;
    unsigned char *compressed_data = NULL;
    unsigned char chunk[CHUNK_SIZE];
    z_stream strm;
    int ret;

    fp = tmpfile();
    if (fp == NULL) {
        fprintf(stderr, "Failed to create temporary file\n");
        return NULL;
    }

    curl = curl_easy_init();
    if (curl) {
        curl_easy_setopt(curl, CURLOPT_URL, url);
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, write_data);
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, fp);
        res = curl_easy_perform(curl);
        curl_easy_cleanup(curl);

        if (res != CURLE_OK) {
            fprintf(stderr, "curl_easy_perform() failed: %s\n", curl_easy_strerror(res));
            fclose(fp);
            return NULL;
        }

        rewind(fp);
        strm.zalloc = Z_NULL;
        strm.zfree = Z_NULL;
        strm.opaque = Z_NULL;
        strm.avail_in = 0;
        strm.next_in = Z_NULL;
        ret = inflateInit2(&strm, MAX_WBITS | 16);
        if (ret != Z_OK) {
            fprintf(stderr, "inflateInit2() failed: %d\n", ret);
            fclose(fp);
            return NULL;
        }

        while (!feof(fp)) {
            strm.avail_in = fread(chunk, 1, CHUNK_SIZE, fp);
            if (ferror(fp)) {
                (void)inflateEnd(&strm);
                fclose(fp);
                return NULL;
            }

            if (strm.avail_in == 0)
                break;

            strm.next_in = chunk;
            do {
                unsigned char out[CHUNK_SIZE];
                strm.avail_out = CHUNK_SIZE;
                strm.next_out = out;
                ret = inflate(&strm, Z_NO_FLUSH);
                if (ret == Z_STREAM_ERROR) {
                    (void)inflateEnd(&strm);
                    fclose(fp);
                    return NULL;
                }

                size_t have = CHUNK_SIZE - strm.avail_out;
                compressed_data = realloc(compressed_data, *data_size + have);
                if (compressed_data == NULL) {
                    (void)inflateEnd(&strm);
                    fclose(fp);
                    return NULL;
                }

                memcpy(compressed_data + *data_size, out, have);
                *data_size += have;
            } while (strm.avail_out == 0);
        }

        (void)inflateEnd(&strm);
        fclose(fp);
    }

    data = compressed_data;
    return data;
}