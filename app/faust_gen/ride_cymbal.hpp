/* ------------------------------------------------------------
name: "ride_cymbal"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn RideCymbal -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __RideCymbal_H__
#define  __RideCymbal_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS RideCymbal
#endif

#ifdef __APPLE__ 
#define exp10f __exp10f
#define exp10 __exp10
#endif

#if defined(_WIN32)
#define RESTRICT __restrict
#else
#define RESTRICT __restrict__
#endif

class RideCymbalSIG0 {
	
  private:
	
	int iVec2[2];
	int iRec5[2];
	
  public:
	
	int getNumInputsRideCymbalSIG0() {
		return 0;
	}
	int getNumOutputsRideCymbalSIG0() {
		return 1;
	}
	
	void instanceInitRideCymbalSIG0(int sample_rate) {
		for (int l7 = 0; l7 < 2; l7 = l7 + 1) {
			iVec2[l7] = 0;
		}
		for (int l8 = 0; l8 < 2; l8 = l8 + 1) {
			iRec5[l8] = 0;
		}
	}
	
	void fillRideCymbalSIG0(int count, float* table) {
		for (int i1 = 0; i1 < count; i1 = i1 + 1) {
			iVec2[0] = 1;
			iRec5[0] = (iVec2[1] + iRec5[1]) % 65536;
			table[i1] = std::sin(9.58738e-05f * float(iRec5[0]));
			iVec2[1] = iVec2[0];
			iRec5[1] = iRec5[0];
		}
	}

};

static RideCymbalSIG0* newRideCymbalSIG0() { return (RideCymbalSIG0*)new RideCymbalSIG0(); }
static void deleteRideCymbalSIG0(RideCymbalSIG0* dsp) { delete dsp; }

static float RideCymbal_faustpower2_f(float value) {
	return value * value;
}
static float ftbl0RideCymbalSIG0[65536];

class RideCymbal : public dsp {
	
 private:
	
	FAUSTFLOAT fButton0;
	float fVec0[2];
	int iVec1[2];
	int iRec0[2];
	int fSampleRate;
	float fConst0;
	float fConst1;
	float fConst2;
	FAUSTFLOAT fHslider0;
	float fConst4;
	float fConst6;
	float fConst8;
	float fConst11;
	float fConst13;
	float fConst15;
	float fConst16;
	float fConst18;
	int iRec4[2];
	float fRec3[3];
	float fConst19;
	float fRec2[3];
	float fConst20;
	float fRec1[3];
	FAUSTFLOAT fHslider1;
	float fConst21;
	float fConst22;
	float fConst23;
	float fConst24;
	FAUSTFLOAT fHslider2;
	float fConst25;
	float fRec6[2];
	float fConst26;
	float fRec7[2];
	FAUSTFLOAT fHslider3;
	float fConst29;
	float fConst31;
	float fConst33;
	float fConst34;
	float fConst35;
	float fRec10[2];
	float fVec3[2];
	int IOTA0;
	float fVec4[64];
	int iConst37;
	int iConst38;
	float fConst40;
	float fConst41;
	float fConst42;
	float fRec11[2];
	float fVec5[2];
	float fVec6[64];
	int iConst44;
	int iConst45;
	float fConst47;
	float fConst48;
	float fConst49;
	float fRec12[2];
	float fVec7[2];
	float fVec8[128];
	int iConst51;
	int iConst52;
	float fConst54;
	float fConst55;
	float fConst56;
	float fRec13[2];
	float fVec9[2];
	float fVec10[128];
	int iConst58;
	int iConst59;
	float fConst61;
	float fConst62;
	float fConst63;
	float fRec14[2];
	float fVec11[2];
	float fVec12[128];
	int iConst65;
	int iConst66;
	float fConst68;
	float fConst69;
	float fConst70;
	float fRec15[2];
	float fVec13[2];
	float fVec14[128];
	int iConst72;
	int iConst73;
	float fConst75;
	float fConst76;
	float fConst77;
	float fRec16[2];
	float fVec15[2];
	float fVec16[256];
	int iConst79;
	int iConst80;
	float fConst82;
	float fConst83;
	float fConst84;
	float fRec17[2];
	float fVec17[2];
	float fVec18[256];
	int iConst86;
	int iConst87;
	float fConst89;
	float fConst90;
	float fConst91;
	float fRec18[2];
	float fVec19[2];
	float fVec20[256];
	int iConst93;
	int iConst94;
	float fConst96;
	float fConst97;
	float fVec21[2];
	float fConst98;
	float fConst99;
	float fRec9[2];
	float fRec8[3];
	float fConst100;
	float fConst101;
	float fConst102;
	float fConst103;
	FAUSTFLOAT fHslider4;
	
 public:
	RideCymbal() {}

	void metadata(Meta* m) { 
		m->declare("basics.lib/name", "Faust Basic Element Library");
		m->declare("basics.lib/tabulateNd", "Copyright (C) 2023 Bart Brouns <bart@magnetophon.nl>");
		m->declare("basics.lib/version", "1.12.0");
		m->declare("compile_options", "-lang cpp -ct 1 -cn RideCymbal -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("envelopes.lib/ar:author", "Yann Orlarey, Stéphane Letz");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "ride_cymbal.dsp");
		m->declare("filters.lib/fir:author", "Julius O. Smith III");
		m->declare("filters.lib/fir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/fir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/highpass:author", "Julius O. Smith III");
		m->declare("filters.lib/highpass:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/iir:author", "Julius O. Smith III");
		m->declare("filters.lib/iir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/iir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1:author", "Julius O. Smith III");
		m->declare("filters.lib/name", "Faust Filters Library");
		m->declare("filters.lib/resonbp:author", "Julius O. Smith III");
		m->declare("filters.lib/resonbp:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/resonbp:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf1:author", "Julius O. Smith III");
		m->declare("filters.lib/tf1:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf1:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf1s:author", "Julius O. Smith III");
		m->declare("filters.lib/tf1s:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf1s:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf2:author", "Julius O. Smith III");
		m->declare("filters.lib/tf2:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf2:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf2s:author", "Julius O. Smith III");
		m->declare("filters.lib/tf2s:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf2s:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/version", "1.3.0");
		m->declare("maths.lib/author", "GRAME");
		m->declare("maths.lib/copyright", "GRAME");
		m->declare("maths.lib/license", "LGPL with exception");
		m->declare("maths.lib/name", "Faust Math Library");
		m->declare("maths.lib/version", "2.7.0");
		m->declare("name", "ride_cymbal");
		m->declare("noises.lib/name", "Faust Noise Generator Library");
		m->declare("noises.lib/version", "1.4.0");
		m->declare("oscillators.lib/lf_sawpos:author", "Bart Brouns, revised by Stéphane Letz");
		m->declare("oscillators.lib/lf_sawpos:licence", "STK-4.3");
		m->declare("oscillators.lib/name", "Faust Oscillator Library");
		m->declare("oscillators.lib/sawN:author", "Julius O. Smith III");
		m->declare("oscillators.lib/sawN:license", "STK-4.3");
		m->declare("oscillators.lib/version", "1.5.0");
		m->declare("platform.lib/name", "Generic Platform Library");
		m->declare("platform.lib/version", "1.3.0");
	}

	virtual int getNumInputs() {
		return 0;
	}
	virtual int getNumOutputs() {
		return 2;
	}
	
	static void classInit(int sample_rate) {
		RideCymbalSIG0* sig0 = newRideCymbalSIG0();
		sig0->instanceInitRideCymbalSIG0(sample_rate);
		sig0->fillRideCymbalSIG0(65536, ftbl0RideCymbalSIG0);
		deleteRideCymbalSIG0(sig0);
	}
	
	virtual void instanceConstants(int sample_rate) {
		fSampleRate = sample_rate;
		fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		fConst1 = std::max<float>(1.0f, 0.003f * fConst0);
		fConst2 = 1.0f / fConst1;
		float fConst3 = std::tan(28902.652f / fConst0);
		fConst4 = 2.0f * (1.0f - 1.0f / RideCymbal_faustpower2_f(fConst3));
		float fConst5 = 1.0f / fConst3;
		fConst6 = (fConst5 + -0.71428573f) / fConst3 + 1.0f;
		float fConst7 = (fConst5 + 0.71428573f) / fConst3 + 1.0f;
		fConst8 = 1.0f / fConst7;
		float fConst9 = std::tan(20420.352f / fConst0);
		float fConst10 = RideCymbal_faustpower2_f(fConst9);
		fConst11 = 2.0f * (1.0f - 1.0f / fConst10);
		float fConst12 = 1.0f / fConst9;
		fConst13 = (fConst12 + -0.76536685f) / fConst9 + 1.0f;
		float fConst14 = (fConst12 + 0.76536685f) / fConst9 + 1.0f;
		fConst15 = 1.0f / fConst14;
		fConst16 = (fConst12 + -1.847759f) / fConst9 + 1.0f;
		float fConst17 = (fConst12 + 1.847759f) / fConst9 + 1.0f;
		fConst18 = 1.0f / fConst17;
		fConst19 = 1.0f / (fConst10 * fConst17);
		fConst20 = 1.0f / (fConst10 * fConst14);
		fConst21 = 0.75f / (fConst3 * fConst7);
		fConst22 = std::max<float>(1.0f, 0.0008f * fConst0);
		fConst23 = 1.0f / fConst22;
		fConst24 = 1.0f / std::max<float>(1.0f, 0.16f * fConst0);
		fConst25 = 7.35f / fConst0;
		fConst26 = 5.0f / fConst0;
		float fConst27 = std::tan(8168.141f / fConst0);
		float fConst28 = RideCymbal_faustpower2_f(fConst27);
		fConst29 = 2.0f * (1.0f - 1.0f / fConst28);
		float fConst30 = 1.0f / fConst27;
		fConst31 = (fConst30 + -1.0f) / fConst27 + 1.0f;
		float fConst32 = (fConst30 + 1.0f) / fConst27 + 1.0f;
		fConst33 = 1.0f / fConst32;
		fConst34 = 1.0f - fConst30;
		fConst35 = 1897.0f / fConst0;
		float fConst36 = std::max<float>(0.0f, std::min<float>(2047.0f, 0.00026357407f * fConst0));
		iConst37 = int(fConst36);
		iConst38 = iConst37 + 1;
		float fConst39 = std::floor(fConst36);
		fConst40 = fConst36 - fConst39;
		fConst41 = fConst39 + (1.0f - fConst36);
		fConst42 = 1621.0f / fConst0;
		float fConst43 = std::max<float>(0.0f, std::min<float>(2047.0f, 0.00030845156f * fConst0));
		iConst44 = int(fConst43);
		iConst45 = iConst44 + 1;
		float fConst46 = std::floor(fConst43);
		fConst47 = fConst43 - fConst46;
		fConst48 = fConst46 + (1.0f - fConst43);
		fConst49 = 1327.0f / fConst0;
		float fConst50 = std::max<float>(0.0f, std::min<float>(2047.0f, 0.00037678974f * fConst0));
		iConst51 = int(fConst50);
		iConst52 = iConst51 + 1;
		float fConst53 = std::floor(fConst50);
		fConst54 = fConst50 - fConst53;
		fConst55 = fConst53 + (1.0f - fConst50);
		fConst56 = 1123.0f / fConst0;
		float fConst57 = std::max<float>(0.0f, std::min<float>(2047.0f, 0.000445236f * fConst0));
		iConst58 = int(fConst57);
		iConst59 = iConst58 + 1;
		float fConst60 = std::floor(fConst57);
		fConst61 = fConst57 - fConst60;
		fConst62 = fConst60 + (1.0f - fConst57);
		fConst63 = 951.0f / fConst0;
		float fConst64 = std::max<float>(0.0f, std::min<float>(2047.0f, 0.0005257623f * fConst0));
		iConst65 = int(fConst64);
		iConst66 = iConst65 + 1;
		float fConst67 = std::floor(fConst64);
		fConst68 = fConst64 - fConst67;
		fConst69 = fConst67 + (1.0f - fConst64);
		fConst70 = 793.0f / fConst0;
		float fConst71 = std::max<float>(0.0f, std::min<float>(2047.0f, 0.000630517f * fConst0));
		iConst72 = int(fConst71);
		iConst73 = iConst72 + 1;
		float fConst74 = std::floor(fConst71);
		fConst75 = fConst71 - fConst74;
		fConst76 = fConst74 + (1.0f - fConst71);
		fConst77 = 638.0f / fConst0;
		float fConst78 = std::max<float>(0.0f, std::min<float>(2047.0f, 0.00078369904f * fConst0));
		iConst79 = int(fConst78);
		iConst80 = iConst79 + 1;
		float fConst81 = std::floor(fConst78);
		fConst82 = fConst78 - fConst81;
		fConst83 = fConst81 + (1.0f - fConst78);
		fConst84 = 527.0f / fConst0;
		float fConst85 = std::max<float>(0.0f, std::min<float>(2047.0f, 0.0009487666f * fConst0));
		iConst86 = int(fConst85);
		iConst87 = iConst86 + 1;
		float fConst88 = std::floor(fConst85);
		fConst89 = fConst85 - fConst88;
		fConst90 = fConst88 + (1.0f - fConst85);
		fConst91 = 411.0f / fConst0;
		float fConst92 = std::max<float>(0.0f, std::min<float>(2047.0f, 0.001216545f * fConst0));
		iConst93 = int(fConst92);
		iConst94 = iConst93 + 1;
		float fConst95 = std::floor(fConst92);
		fConst96 = fConst92 - fConst95;
		fConst97 = fConst95 + (1.0f - fConst92);
		fConst98 = 0.11111111f * (fConst0 / fConst27);
		fConst99 = 1.0f / (fConst30 + 1.0f);
		fConst100 = std::max<float>(1.0f, 0.0007f * fConst0);
		fConst101 = 1.0f / fConst100;
		fConst102 = 0.55f * fConst0;
		fConst103 = 1.0f / (fConst28 * fConst32);
	}
	
	virtual void instanceResetUserInterface() {
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider0 = FAUSTFLOAT(2.2f);
		fHslider1 = FAUSTFLOAT(0.7f);
		fHslider2 = FAUSTFLOAT(4.4e+02f);
		fHslider3 = FAUSTFLOAT(0.6f);
		fHslider4 = FAUSTFLOAT(0.6f);
	}
	
	virtual void instanceClear() {
		for (int l0 = 0; l0 < 2; l0 = l0 + 1) {
			fVec0[l0] = 0.0f;
		}
		for (int l1 = 0; l1 < 2; l1 = l1 + 1) {
			iVec1[l1] = 0;
		}
		for (int l2 = 0; l2 < 2; l2 = l2 + 1) {
			iRec0[l2] = 0;
		}
		for (int l3 = 0; l3 < 2; l3 = l3 + 1) {
			iRec4[l3] = 0;
		}
		for (int l4 = 0; l4 < 3; l4 = l4 + 1) {
			fRec3[l4] = 0.0f;
		}
		for (int l5 = 0; l5 < 3; l5 = l5 + 1) {
			fRec2[l5] = 0.0f;
		}
		for (int l6 = 0; l6 < 3; l6 = l6 + 1) {
			fRec1[l6] = 0.0f;
		}
		for (int l9 = 0; l9 < 2; l9 = l9 + 1) {
			fRec6[l9] = 0.0f;
		}
		for (int l10 = 0; l10 < 2; l10 = l10 + 1) {
			fRec7[l10] = 0.0f;
		}
		for (int l11 = 0; l11 < 2; l11 = l11 + 1) {
			fRec10[l11] = 0.0f;
		}
		for (int l12 = 0; l12 < 2; l12 = l12 + 1) {
			fVec3[l12] = 0.0f;
		}
		IOTA0 = 0;
		for (int l13 = 0; l13 < 64; l13 = l13 + 1) {
			fVec4[l13] = 0.0f;
		}
		for (int l14 = 0; l14 < 2; l14 = l14 + 1) {
			fRec11[l14] = 0.0f;
		}
		for (int l15 = 0; l15 < 2; l15 = l15 + 1) {
			fVec5[l15] = 0.0f;
		}
		for (int l16 = 0; l16 < 64; l16 = l16 + 1) {
			fVec6[l16] = 0.0f;
		}
		for (int l17 = 0; l17 < 2; l17 = l17 + 1) {
			fRec12[l17] = 0.0f;
		}
		for (int l18 = 0; l18 < 2; l18 = l18 + 1) {
			fVec7[l18] = 0.0f;
		}
		for (int l19 = 0; l19 < 128; l19 = l19 + 1) {
			fVec8[l19] = 0.0f;
		}
		for (int l20 = 0; l20 < 2; l20 = l20 + 1) {
			fRec13[l20] = 0.0f;
		}
		for (int l21 = 0; l21 < 2; l21 = l21 + 1) {
			fVec9[l21] = 0.0f;
		}
		for (int l22 = 0; l22 < 128; l22 = l22 + 1) {
			fVec10[l22] = 0.0f;
		}
		for (int l23 = 0; l23 < 2; l23 = l23 + 1) {
			fRec14[l23] = 0.0f;
		}
		for (int l24 = 0; l24 < 2; l24 = l24 + 1) {
			fVec11[l24] = 0.0f;
		}
		for (int l25 = 0; l25 < 128; l25 = l25 + 1) {
			fVec12[l25] = 0.0f;
		}
		for (int l26 = 0; l26 < 2; l26 = l26 + 1) {
			fRec15[l26] = 0.0f;
		}
		for (int l27 = 0; l27 < 2; l27 = l27 + 1) {
			fVec13[l27] = 0.0f;
		}
		for (int l28 = 0; l28 < 128; l28 = l28 + 1) {
			fVec14[l28] = 0.0f;
		}
		for (int l29 = 0; l29 < 2; l29 = l29 + 1) {
			fRec16[l29] = 0.0f;
		}
		for (int l30 = 0; l30 < 2; l30 = l30 + 1) {
			fVec15[l30] = 0.0f;
		}
		for (int l31 = 0; l31 < 256; l31 = l31 + 1) {
			fVec16[l31] = 0.0f;
		}
		for (int l32 = 0; l32 < 2; l32 = l32 + 1) {
			fRec17[l32] = 0.0f;
		}
		for (int l33 = 0; l33 < 2; l33 = l33 + 1) {
			fVec17[l33] = 0.0f;
		}
		for (int l34 = 0; l34 < 256; l34 = l34 + 1) {
			fVec18[l34] = 0.0f;
		}
		for (int l35 = 0; l35 < 2; l35 = l35 + 1) {
			fRec18[l35] = 0.0f;
		}
		for (int l36 = 0; l36 < 2; l36 = l36 + 1) {
			fVec19[l36] = 0.0f;
		}
		for (int l37 = 0; l37 < 256; l37 = l37 + 1) {
			fVec20[l37] = 0.0f;
		}
		for (int l38 = 0; l38 < 2; l38 = l38 + 1) {
			fVec21[l38] = 0.0f;
		}
		for (int l39 = 0; l39 < 2; l39 = l39 + 1) {
			fRec9[l39] = 0.0f;
		}
		for (int l40 = 0; l40 < 3; l40 = l40 + 1) {
			fRec8[l40] = 0.0f;
		}
	}
	
	virtual void init(int sample_rate) {
		classInit(sample_rate);
		instanceInit(sample_rate);
	}
	
	virtual void instanceInit(int sample_rate) {
		instanceConstants(sample_rate);
		instanceResetUserInterface();
		instanceClear();
	}
	
	virtual RideCymbal* clone() {
		return new RideCymbal();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("ride_cymbal");
		ui_interface->addHorizontalSlider("decay", &fHslider0, FAUSTFLOAT(2.2f), FAUSTFLOAT(0.5f), FAUSTFLOAT(4.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("freq", &fHslider2, FAUSTFLOAT(4.4e+02f), FAUSTFLOAT(2e+01f), FAUSTFLOAT(2e+03f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("gain", &fHslider4, FAUSTFLOAT(0.6f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->addHorizontalSlider("ping", &fHslider3, FAUSTFLOAT(0.6f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.5f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("wash", &fHslider1, FAUSTFLOAT(0.7f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.5f), FAUSTFLOAT(0.01f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = float(fButton0);
		float fSlow1 = float(fHslider0);
		float fSlow2 = 1.0f / std::max<float>(1.0f, fConst0 * fSlow1);
		float fSlow3 = fConst21 * float(fHslider1);
		float fSlow4 = float(fHslider2);
		float fSlow5 = fConst25 * fSlow4;
		float fSlow6 = fConst26 * fSlow4;
		float fSlow7 = 0.55f * float(fHslider3);
		float fSlow8 = 1.0f / std::max<float>(1.0f, fConst102 * fSlow1);
		float fSlow9 = 0.55f * float(fHslider4);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			fVec0[0] = fSlow0;
			iVec1[0] = 1;
			iRec0[0] = (iRec0[1] + (iRec0[1] > 0)) * (fSlow0 <= fVec0[1]) + (fSlow0 > fVec0[1]);
			float fTemp0 = float(iRec0[0]);
			iRec4[0] = 1103515245 * iRec4[1] + 12345;
			fRec3[0] = 4.656613e-10f * float(iRec4[0]) - fConst18 * (fConst16 * fRec3[2] + fConst11 * fRec3[1]);
			fRec2[0] = fConst19 * (fRec3[2] + (fRec3[0] - 2.0f * fRec3[1])) - fConst15 * (fConst13 * fRec2[2] + fConst11 * fRec2[1]);
			fRec1[0] = fConst20 * (fRec2[2] + (fRec2[0] - 2.0f * fRec2[1])) - fConst8 * (fConst6 * fRec1[2] + fConst4 * fRec1[1]);
			int iTemp1 = 1 - iVec1[1];
			float fTemp2 = ((iTemp1) ? 0.0f : fSlow5 + fRec6[1]);
			fRec6[0] = fTemp2 - std::floor(fTemp2);
			float fTemp3 = ((iTemp1) ? 0.0f : fSlow6 + fRec7[1]);
			fRec7[0] = fTemp3 - std::floor(fTemp3);
			float fTemp4 = ((iTemp1) ? 0.0f : fConst35 + fRec10[1]);
			fRec10[0] = fTemp4 - std::floor(fTemp4);
			float fTemp5 = RideCymbal_faustpower2_f(2.0f * fRec10[0] + -1.0f);
			fVec3[0] = fTemp5;
			float fTemp6 = float(iVec1[1]);
			float fTemp7 = fTemp6 * (fTemp5 - fVec3[1]);
			fVec4[IOTA0 & 63] = fTemp7;
			float fTemp8 = ((iTemp1) ? 0.0f : fConst42 + fRec11[1]);
			fRec11[0] = fTemp8 - std::floor(fTemp8);
			float fTemp9 = RideCymbal_faustpower2_f(2.0f * fRec11[0] + -1.0f);
			fVec5[0] = fTemp9;
			float fTemp10 = fTemp6 * (fTemp9 - fVec5[1]);
			fVec6[IOTA0 & 63] = fTemp10;
			float fTemp11 = ((iTemp1) ? 0.0f : fConst49 + fRec12[1]);
			fRec12[0] = fTemp11 - std::floor(fTemp11);
			float fTemp12 = RideCymbal_faustpower2_f(2.0f * fRec12[0] + -1.0f);
			fVec7[0] = fTemp12;
			float fTemp13 = fTemp6 * (fTemp12 - fVec7[1]);
			fVec8[IOTA0 & 127] = fTemp13;
			float fTemp14 = ((iTemp1) ? 0.0f : fConst56 + fRec13[1]);
			fRec13[0] = fTemp14 - std::floor(fTemp14);
			float fTemp15 = RideCymbal_faustpower2_f(2.0f * fRec13[0] + -1.0f);
			fVec9[0] = fTemp15;
			float fTemp16 = fTemp6 * (fTemp15 - fVec9[1]);
			fVec10[IOTA0 & 127] = fTemp16;
			float fTemp17 = ((iTemp1) ? 0.0f : fConst63 + fRec14[1]);
			fRec14[0] = fTemp17 - std::floor(fTemp17);
			float fTemp18 = RideCymbal_faustpower2_f(2.0f * fRec14[0] + -1.0f);
			fVec11[0] = fTemp18;
			float fTemp19 = fTemp6 * (fTemp18 - fVec11[1]);
			fVec12[IOTA0 & 127] = fTemp19;
			float fTemp20 = ((iTemp1) ? 0.0f : fConst70 + fRec15[1]);
			fRec15[0] = fTemp20 - std::floor(fTemp20);
			float fTemp21 = RideCymbal_faustpower2_f(2.0f * fRec15[0] + -1.0f);
			fVec13[0] = fTemp21;
			float fTemp22 = fTemp6 * (fTemp21 - fVec13[1]);
			fVec14[IOTA0 & 127] = fTemp22;
			float fTemp23 = ((iTemp1) ? 0.0f : fConst77 + fRec16[1]);
			fRec16[0] = fTemp23 - std::floor(fTemp23);
			float fTemp24 = RideCymbal_faustpower2_f(2.0f * fRec16[0] + -1.0f);
			fVec15[0] = fTemp24;
			float fTemp25 = fTemp6 * (fTemp24 - fVec15[1]);
			fVec16[IOTA0 & 255] = fTemp25;
			float fTemp26 = ((iTemp1) ? 0.0f : fConst84 + fRec17[1]);
			fRec17[0] = fTemp26 - std::floor(fTemp26);
			float fTemp27 = RideCymbal_faustpower2_f(2.0f * fRec17[0] + -1.0f);
			fVec17[0] = fTemp27;
			float fTemp28 = fTemp6 * (fTemp27 - fVec17[1]);
			fVec18[IOTA0 & 255] = fTemp28;
			float fTemp29 = ((iTemp1) ? 0.0f : fConst91 + fRec18[1]);
			fRec18[0] = fTemp29 - std::floor(fTemp29);
			float fTemp30 = RideCymbal_faustpower2_f(2.0f * fRec18[0] + -1.0f);
			fVec19[0] = fTemp30;
			float fTemp31 = fTemp6 * (fTemp30 - fVec19[1]);
			fVec20[IOTA0 & 255] = fTemp31;
			float fTemp32 = 0.0006082725f * (fTemp31 - fConst97 * fVec20[(IOTA0 - iConst93) & 255] - fConst96 * fVec20[(IOTA0 - iConst94) & 255]) + 0.0004743833f * (fTemp28 - fConst90 * fVec18[(IOTA0 - iConst86) & 255] - fConst89 * fVec18[(IOTA0 - iConst87) & 255]) + 0.00039184952f * (fTemp25 - fConst83 * fVec16[(IOTA0 - iConst79) & 255] - fConst82 * fVec16[(IOTA0 - iConst80) & 255]) + 0.0003152585f * (fTemp22 - fConst76 * fVec14[(IOTA0 - iConst72) & 127] - fConst75 * fVec14[(IOTA0 - iConst73) & 127]) + 0.00026288116f * (fTemp19 - fConst69 * fVec12[(IOTA0 - iConst65) & 127] - fConst68 * fVec12[(IOTA0 - iConst66) & 127]) + 0.000222618f * (fTemp16 - fConst62 * fVec10[(IOTA0 - iConst58) & 127] - fConst61 * fVec10[(IOTA0 - iConst59) & 127]) + 0.00018839487f * (fTemp13 - fConst55 * fVec8[(IOTA0 - iConst51) & 127] - fConst54 * fVec8[(IOTA0 - iConst52) & 127]) + 0.00015422578f * (fTemp10 - fConst48 * fVec6[(IOTA0 - iConst44) & 63] - fConst47 * fVec6[(IOTA0 - iConst45) & 63]) + 0.00013178703f * (fTemp7 - fConst41 * fVec4[(IOTA0 - iConst37) & 63] - fConst40 * fVec4[(IOTA0 - iConst38) & 63]);
			fVec21[0] = fTemp32;
			fRec9[0] = fConst99 * (fConst98 * (fTemp32 - fVec21[1]) - fConst34 * fRec9[1]);
			fRec8[0] = fRec9[0] - fConst33 * (fConst31 * fRec8[2] + fConst29 * fRec8[1]);
			float fTemp33 = fSlow9 * (fConst103 * std::max<float>(0.0f, std::min<float>(fConst101 * fTemp0, fSlow8 * (fConst100 - fTemp0) + 1.0f)) * (fRec8[0] + fRec8[2] - 2.0f * fRec8[1]) + fSlow7 * (ftbl0RideCymbalSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec7[0]), 65535))] + 0.6f * ftbl0RideCymbalSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec6[0]), 65535))]) * std::max<float>(0.0f, std::min<float>(fConst23 * fTemp0, fConst24 * (fConst22 - fTemp0) + 1.0f)) + fSlow3 * (fRec1[0] - fRec1[2]) * std::max<float>(0.0f, std::min<float>(fConst2 * fTemp0, fSlow2 * (fConst1 - fTemp0) + 1.0f)));
			output0[i0] = FAUSTFLOAT(fTemp33);
			output1[i0] = FAUSTFLOAT(fTemp33);
			fVec0[1] = fVec0[0];
			iVec1[1] = iVec1[0];
			iRec0[1] = iRec0[0];
			iRec4[1] = iRec4[0];
			fRec3[2] = fRec3[1];
			fRec3[1] = fRec3[0];
			fRec2[2] = fRec2[1];
			fRec2[1] = fRec2[0];
			fRec1[2] = fRec1[1];
			fRec1[1] = fRec1[0];
			fRec6[1] = fRec6[0];
			fRec7[1] = fRec7[0];
			fRec10[1] = fRec10[0];
			fVec3[1] = fVec3[0];
			IOTA0 = IOTA0 + 1;
			fRec11[1] = fRec11[0];
			fVec5[1] = fVec5[0];
			fRec12[1] = fRec12[0];
			fVec7[1] = fVec7[0];
			fRec13[1] = fRec13[0];
			fVec9[1] = fVec9[0];
			fRec14[1] = fRec14[0];
			fVec11[1] = fVec11[0];
			fRec15[1] = fRec15[0];
			fVec13[1] = fVec13[0];
			fRec16[1] = fRec16[0];
			fVec15[1] = fVec15[0];
			fRec17[1] = fRec17[0];
			fVec17[1] = fVec17[0];
			fRec18[1] = fRec18[0];
			fVec19[1] = fVec19[0];
			fVec21[1] = fVec21[0];
			fRec9[1] = fRec9[0];
			fRec8[2] = fRec8[1];
			fRec8[1] = fRec8[0];
		}
	}

};

#endif
