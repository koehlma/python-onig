typedef struct OnigEncodingTypeST { ...; } OnigEncodingType;

typedef OnigEncodingType *OnigEncoding;

extern OnigEncodingType OnigEncodingASCII;

extern OnigEncodingType OnigEncodingISO_8859_1;

extern OnigEncodingType OnigEncodingUTF8;

extern OnigEncodingType OnigEncodingUTF16_BE;
extern OnigEncodingType OnigEncodingUTF16_LE;
extern OnigEncodingType OnigEncodingUTF32_BE;
extern OnigEncodingType OnigEncodingUTF32_LE;


#define ONIG_NORMAL ...

#define ONIG_OPTION_NONE ...

#define ONIG_OPTION_IGNORECASE ...
#define ONIG_OPTION_EXTEND ...
#define ONIG_OPTION_MULTILINE ...
#define ONIG_OPTION_SINGLELINE ...
#define ONIG_OPTION_FIND_LONGEST ...
#define ONIG_OPTION_FIND_NOT_EMPTY ...
#define ONIG_OPTION_NEGATE_SINGLELINE ...
#define ONIG_OPTION_DONT_CAPTURE_GROUP ...
#define ONIG_OPTION_CAPTURE_GROUP ...


typedef int OnigOptionType;

typedef unsigned char OnigUChar;

typedef ... OnigRegexType;
typedef OnigRegexType*  OnigRegex;

typedef struct re_registers {
    int  num_regs;
    int* beg;
    int* end;
    ...;
} OnigRegion;

typedef struct { ...; } OnigErrorInfo;


extern int onig_initialize(OnigEncoding [], int);


OnigRegion *onig_region_new(void);


int onig_cffi_new(
    OnigRegex *,
    const OnigUChar *,
    size_t,
    OnigOptionType,
    OnigEncoding,
    OnigErrorInfo *);


void onig_cffi_region_free(OnigRegion *);

int onig_cffi_search(
    OnigRegex *,
    const OnigUChar *,
    size_t,
    size_t,
    OnigRegion *,
    OnigOptionType
);


int onig_cffi_name_to_group_numbers(
    OnigRegex *,
    const OnigUChar *,
    size_t,
    int **number_list
);
