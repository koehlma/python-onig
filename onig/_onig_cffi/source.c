#define ONIG_EXTERN extern

#include <oniguruma.h>

int onig_cffi_new(
    OnigRegex *regex,
    const OnigUChar *pattern,
    size_t length,
    OnigOptionType options,
    OnigEncoding encoding,
    OnigErrorInfo *error_info
) {
    return onig_new(
        regex,
        pattern,
        pattern + length,
        options,
        encoding,
        ONIG_SYNTAX_ONIGURUMA,
        error_info
    );
}

void onig_cffi_region_free(OnigRegion *region) {
    onig_region_free(region, 1);
}

int onig_cffi_search(
    OnigRegex *regex,
    const OnigUChar *text,
    size_t length,
    size_t start,
    OnigRegion* region,
    OnigOptionType options
) {
    return onig_search(
        *regex,
        text,
        text + length,
        text + start,
        text + length,
        region,
        options
    );
}


int onig_cffi_name_to_group_numbers(
    OnigRegex *regex,
    const OnigUChar *name,
    size_t length,
    int **number_list
) {
    return onig_name_to_group_numbers(
        *regex,
        name,
        name + length,
        number_list
    );
}