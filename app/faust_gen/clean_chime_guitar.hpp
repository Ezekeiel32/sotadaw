/* ------------------------------------------------------------
name: "clean_chime_guitar"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn CleanChimeGuitar -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __CleanChimeGuitar_H__
#define  __CleanChimeGuitar_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS CleanChimeGuitar
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

class CleanChimeGuitarSIG0 {
	
  private:
	
	int iVec6[2];
	int iRec10[2];
	
  public:
	
	int getNumInputsCleanChimeGuitarSIG0() {
		return 0;
	}
	int getNumOutputsCleanChimeGuitarSIG0() {
		return 1;
	}
	
	void instanceInitCleanChimeGuitarSIG0(int sample_rate) {
		for (int l15 = 0; l15 < 2; l15 = l15 + 1) {
			iVec6[l15] = 0;
		}
		for (int l16 = 0; l16 < 2; l16 = l16 + 1) {
			iRec10[l16] = 0;
		}
	}
	
	void fillCleanChimeGuitarSIG0(int count, float* table) {
		for (int i1 = 0; i1 < count; i1 = i1 + 1) {
			iVec6[0] = 1;
			iRec10[0] = (iVec6[1] + iRec10[1]) % 65536;
			table[i1] = std::sin(9.58738e-05f * float(iRec10[0]));
			iVec6[1] = iVec6[0];
			iRec10[1] = iRec10[0];
		}
	}

};

static CleanChimeGuitarSIG0* newCleanChimeGuitarSIG0() { return (CleanChimeGuitarSIG0*)new CleanChimeGuitarSIG0(); }
static void deleteCleanChimeGuitarSIG0(CleanChimeGuitarSIG0* dsp) { delete dsp; }

static float ftbl0CleanChimeGuitarSIG0[65536];

class CleanChimeGuitar : public dsp {
	
 private:
	
	int iVec0[2];
	FAUSTFLOAT fHslider0;
	int fSampleRate;
	float fConst0;
	float fConst1;
	float fRec3[2];
	float fConst2;
	float fConst3;
	float fConst4;
	float fRec2[2];
	FAUSTFLOAT fHslider1;
	FAUSTFLOAT fButton0;
	float fVec1[2];
	int iRec5[2];
	float fConst5;
	float fConst6;
	float fConst7;
	float fConst8;
	float fConst9;
	float fConst10;
	int iRec6[2];
	float fVec2[2];
	float fConst11;
	float fConst12;
	float fConst13;
	float fRec4[2];
	int IOTA0;
	float fVec3[8192];
	FAUSTFLOAT fHslider2;
	FAUSTFLOAT fHslider3;
	float fRec1[3];
	float fRec9[2];
	float fRec8[2];
	float fVec4[8192];
	float fRec7[3];
	float fVec5[32];
	float fConst14;
	float fRec11[2];
	float fVec7[2];
	float fConst16;
	float fConst17;
	float fRec0[2];
	FAUSTFLOAT fHslider4;
	
 public:
	CleanChimeGuitar() {}

	void metadata(Meta* m) { 
		m->declare("basics.lib/name", "Faust Basic Element Library");
		m->declare("basics.lib/tabulateNd", "Copyright (C) 2023 Bart Brouns <bart@magnetophon.nl>");
		m->declare("basics.lib/version", "1.12.0");
		m->declare("compile_options", "-lang cpp -ct 1 -cn CleanChimeGuitar -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("delays.lib/fdelay4:author", "Julius O. Smith III");
		m->declare("delays.lib/fdelayltv:author", "Julius O. Smith III");
		m->declare("delays.lib/name", "Faust Delay Library");
		m->declare("delays.lib/version", "1.1.0");
		m->declare("envelopes.lib/ar:author", "Yann Orlarey, Stéphane Letz");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "clean_chime_guitar.dsp");
		m->declare("filters.lib/highpass:author", "Julius O. Smith III");
		m->declare("filters.lib/highpass:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/lowpass0_highpass1", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1:author", "Julius O. Smith III");
		m->declare("filters.lib/lowpass:author", "Julius O. Smith III");
		m->declare("filters.lib/lowpass:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/lowpass:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/name", "Faust Filters Library");
		m->declare("filters.lib/tf1:author", "Julius O. Smith III");
		m->declare("filters.lib/tf1:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf1:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf1s:author", "Julius O. Smith III");
		m->declare("filters.lib/tf1s:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf1s:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/version", "1.3.0");
		m->declare("maths.lib/author", "GRAME");
		m->declare("maths.lib/copyright", "GRAME");
		m->declare("maths.lib/license", "LGPL with exception");
		m->declare("maths.lib/name", "Faust Math Library");
		m->declare("maths.lib/version", "2.7.0");
		m->declare("name", "clean_chime_guitar");
		m->declare("noises.lib/name", "Faust Noise Generator Library");
		m->declare("noises.lib/version", "1.4.0");
		m->declare("oscillators.lib/name", "Faust Oscillator Library");
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
		CleanChimeGuitarSIG0* sig0 = newCleanChimeGuitarSIG0();
		sig0->instanceInitCleanChimeGuitarSIG0(sample_rate);
		sig0->fillCleanChimeGuitarSIG0(65536, ftbl0CleanChimeGuitarSIG0);
		deleteCleanChimeGuitarSIG0(sig0);
	}
	
	virtual void instanceConstants(int sample_rate) {
		fSampleRate = sample_rate;
		fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		fConst1 = 3.1415927f / fConst0;
		fConst2 = 1.0f / std::tan(314.15927f / fConst0);
		fConst3 = 1.0f - fConst2;
		fConst4 = 1.0f / (fConst2 + 1.0f);
		fConst5 = std::max<float>(1.0f, 0.0002f * fConst0);
		fConst6 = 1.0f / fConst5;
		fConst7 = 1.0f / std::max<float>(1.0f, 0.004f * fConst0);
		fConst8 = std::max<float>(1.0f, 0.0006f * fConst0);
		fConst9 = 1.0f / fConst8;
		fConst10 = 1.0f / std::max<float>(1.0f, 0.01f * fConst0);
		fConst11 = 1.0f / std::tan(502.65482f / fConst0);
		fConst12 = 1.0f - fConst11;
		fConst13 = 1.0f / (fConst11 + 1.0f);
		fConst14 = 0.45f / fConst0;
		float fConst15 = 1.0f / std::tan(34557.52f / fConst0);
		fConst16 = 1.0f - fConst15;
		fConst17 = 1.0f / (fConst15 + 1.0f);
	}
	
	virtual void instanceResetUserInterface() {
		fHslider0 = FAUSTFLOAT(8e+03f);
		fHslider1 = FAUSTFLOAT(0.996f);
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider2 = FAUSTFLOAT(4.4e+02f);
		fHslider3 = FAUSTFLOAT(0.5f);
		fHslider4 = FAUSTFLOAT(0.7f);
	}
	
	virtual void instanceClear() {
		for (int l0 = 0; l0 < 2; l0 = l0 + 1) {
			iVec0[l0] = 0;
		}
		for (int l1 = 0; l1 < 2; l1 = l1 + 1) {
			fRec3[l1] = 0.0f;
		}
		for (int l2 = 0; l2 < 2; l2 = l2 + 1) {
			fRec2[l2] = 0.0f;
		}
		for (int l3 = 0; l3 < 2; l3 = l3 + 1) {
			fVec1[l3] = 0.0f;
		}
		for (int l4 = 0; l4 < 2; l4 = l4 + 1) {
			iRec5[l4] = 0;
		}
		for (int l5 = 0; l5 < 2; l5 = l5 + 1) {
			iRec6[l5] = 0;
		}
		for (int l6 = 0; l6 < 2; l6 = l6 + 1) {
			fVec2[l6] = 0.0f;
		}
		for (int l7 = 0; l7 < 2; l7 = l7 + 1) {
			fRec4[l7] = 0.0f;
		}
		IOTA0 = 0;
		for (int l8 = 0; l8 < 8192; l8 = l8 + 1) {
			fVec3[l8] = 0.0f;
		}
		for (int l9 = 0; l9 < 3; l9 = l9 + 1) {
			fRec1[l9] = 0.0f;
		}
		for (int l10 = 0; l10 < 2; l10 = l10 + 1) {
			fRec9[l10] = 0.0f;
		}
		for (int l11 = 0; l11 < 2; l11 = l11 + 1) {
			fRec8[l11] = 0.0f;
		}
		for (int l12 = 0; l12 < 8192; l12 = l12 + 1) {
			fVec4[l12] = 0.0f;
		}
		for (int l13 = 0; l13 < 3; l13 = l13 + 1) {
			fRec7[l13] = 0.0f;
		}
		for (int l14 = 0; l14 < 32; l14 = l14 + 1) {
			fVec5[l14] = 0.0f;
		}
		for (int l17 = 0; l17 < 2; l17 = l17 + 1) {
			fRec11[l17] = 0.0f;
		}
		for (int l18 = 0; l18 < 2; l18 = l18 + 1) {
			fVec7[l18] = 0.0f;
		}
		for (int l19 = 0; l19 < 2; l19 = l19 + 1) {
			fRec0[l19] = 0.0f;
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
	
	virtual CleanChimeGuitar* clone() {
		return new CleanChimeGuitar();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("clean_chime_guitar");
		ui_interface->addHorizontalSlider("chorus", &fHslider3, FAUSTFLOAT(0.5f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("damp", &fHslider0, FAUSTFLOAT(8e+03f), FAUSTFLOAT(1e+03f), FAUSTFLOAT(1.2e+04f), FAUSTFLOAT(1.0f));
		ui_interface->addHorizontalSlider("freq", &fHslider2, FAUSTFLOAT(4.4e+02f), FAUSTFLOAT(4e+01f), FAUSTFLOAT(3e+03f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("gain", &fHslider4, FAUSTFLOAT(0.7f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->addHorizontalSlider("sustain", &fHslider1, FAUSTFLOAT(0.996f), FAUSTFLOAT(0.9f), FAUSTFLOAT(0.999f), FAUSTFLOAT(0.0001f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = 1.0f / std::tan(fConst1 * float(fHslider0));
		float fSlow1 = 1.0f - fSlow0;
		float fSlow2 = 1.0f / (fSlow0 + 1.0f);
		float fSlow3 = float(fHslider1);
		float fSlow4 = float(fButton0);
		float fSlow5 = float(fHslider2);
		float fSlow6 = float(fHslider3);
		float fSlow7 = fConst0 / ((0.004f * fSlow6 + 1.0f) * fSlow5);
		float fSlow8 = fSlow7 + -2.499995f;
		int iSlow9 = int(fSlow8);
		int iSlow10 = std::min<int>(4096, std::max<int>(0, iSlow9 + 4));
		float fSlow11 = std::floor(fSlow8);
		float fSlow12 = fSlow7 + (-4.0f - fSlow11);
		float fSlow13 = fSlow7 + (-3.0f - fSlow11);
		float fSlow14 = fSlow7 + (-2.0f - fSlow11);
		float fSlow15 = fSlow7 + (-1.0f - fSlow11);
		float fSlow16 = fSlow15 * fSlow14;
		float fSlow17 = fSlow16 * fSlow13;
		float fSlow18 = 0.041666668f * fSlow17 * fSlow12;
		int iSlow19 = std::min<int>(4096, std::max<int>(0, iSlow9 + 3));
		float fSlow20 = 0.16666667f * fSlow17;
		int iSlow21 = std::min<int>(4096, std::max<int>(0, iSlow9 + 2));
		float fSlow22 = 0.25f * fSlow16;
		int iSlow23 = std::min<int>(4096, std::max<int>(0, iSlow9 + 1));
		float fSlow24 = 0.16666667f * fSlow15;
		int iSlow25 = std::min<int>(4096, std::max<int>(0, iSlow9));
		float fSlow26 = 0.041666668f * fSlow14;
		float fSlow27 = fSlow7 + (-5.0f - fSlow11);
		float fSlow28 = fConst0 / fSlow5;
		float fSlow29 = fSlow28 + -2.499995f;
		int iSlow30 = int(fSlow29);
		int iSlow31 = std::min<int>(4096, std::max<int>(0, iSlow30 + 4));
		float fSlow32 = std::floor(fSlow29);
		float fSlow33 = fSlow28 + (-4.0f - fSlow32);
		float fSlow34 = fSlow28 + (-3.0f - fSlow32);
		float fSlow35 = fSlow28 + (-2.0f - fSlow32);
		float fSlow36 = fSlow28 + (-1.0f - fSlow32);
		float fSlow37 = fSlow36 * fSlow35;
		float fSlow38 = fSlow37 * fSlow34;
		float fSlow39 = 0.041666668f * fSlow38 * fSlow33;
		int iSlow40 = std::min<int>(4096, std::max<int>(0, iSlow30 + 3));
		float fSlow41 = 0.16666667f * fSlow38;
		int iSlow42 = std::min<int>(4096, std::max<int>(0, iSlow30 + 2));
		float fSlow43 = 0.25f * fSlow37;
		int iSlow44 = std::min<int>(4096, std::max<int>(0, iSlow30 + 1));
		float fSlow45 = 0.16666667f * fSlow36;
		int iSlow46 = std::min<int>(4096, std::max<int>(0, iSlow30));
		float fSlow47 = 0.041666668f * fSlow35;
		float fSlow48 = fSlow28 + (-5.0f - fSlow32);
		float fSlow49 = 5.0f * fSlow6 + 1.0f;
		float fSlow50 = 0.225f * fSlow6;
		float fSlow51 = 0.5f * (1.0f - 0.45f * fSlow6);
		float fSlow52 = 0.55f * float(fHslider4);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			iVec0[0] = 1;
			fRec3[0] = -(fSlow2 * (fSlow1 * fRec3[1] - (fRec1[1] + fRec1[2])));
			fRec2[0] = -(fConst4 * (fConst3 * fRec2[1] - fConst2 * (fRec3[0] - fRec3[1])));
			fVec1[0] = fSlow4;
			iRec5[0] = (iRec5[1] + (iRec5[1] > 0)) * (fSlow4 <= fVec1[1]) + (fSlow4 > fVec1[1]);
			float fTemp0 = float(iRec5[0]);
			iRec6[0] = 1103515245 * iRec6[1] + 12345;
			float fTemp1 = float(iRec6[0]) * (4.656613e-10f * std::max<float>(0.0f, std::min<float>(fConst9 * fTemp0, fConst10 * (fConst8 - fTemp0) + 1.0f)) + 1.8626452e-10f * std::max<float>(0.0f, std::min<float>(fConst6 * fTemp0, fConst7 * (fConst5 - fTemp0) + 1.0f)));
			fVec2[0] = fTemp1;
			fRec4[0] = -(fConst13 * (fConst12 * fRec4[1] - fConst11 * (fTemp1 - fVec2[1])));
			float fTemp2 = fRec4[0] + fSlow3 * fRec2[0];
			fVec3[IOTA0 & 8191] = fTemp2;
			fRec1[0] = fSlow27 * (fSlow12 * (fSlow13 * (fSlow26 * fVec3[(IOTA0 - iSlow25) & 8191] - fSlow24 * fVec3[(IOTA0 - iSlow23) & 8191]) + fSlow22 * fVec3[(IOTA0 - iSlow21) & 8191]) - fSlow20 * fVec3[(IOTA0 - iSlow19) & 8191]) + fSlow18 * fVec3[(IOTA0 - iSlow10) & 8191];
			fRec9[0] = -(fSlow2 * (fSlow1 * fRec9[1] - (fRec7[1] + fRec7[2])));
			fRec8[0] = -(fConst4 * (fConst3 * fRec8[1] - fConst2 * (fRec9[0] - fRec9[1])));
			float fTemp3 = fRec4[0] + fSlow3 * fRec8[0];
			fVec4[IOTA0 & 8191] = fTemp3;
			fRec7[0] = fSlow48 * (fSlow33 * (fSlow34 * (fSlow47 * fVec4[(IOTA0 - iSlow46) & 8191] - fSlow45 * fVec4[(IOTA0 - iSlow44) & 8191]) + fSlow43 * fVec4[(IOTA0 - iSlow42) & 8191]) - fSlow41 * fVec4[(IOTA0 - iSlow40) & 8191]) + fSlow39 * fVec4[(IOTA0 - iSlow31) & 8191];
			float fTemp4 = fRec7[0] + fRec1[0];
			fVec5[IOTA0 & 31] = fTemp4;
			float fTemp5 = ((1 - iVec0[1]) ? 0.0f : fConst14 + fRec11[1]);
			fRec11[0] = fTemp5 - std::floor(fTemp5);
			float fTemp6 = fSlow49 * ftbl0CleanChimeGuitarSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec11[0]), 65535))];
			float fTemp7 = fTemp6 + 22.0f;
			int iTemp8 = int(fTemp7);
			float fTemp9 = std::floor(fTemp7);
			float fTemp10 = fSlow51 * fTemp4 + fSlow50 * (fVec5[(IOTA0 - std::min<int>(2049, std::max<int>(0, iTemp8))) & 31] * (fTemp9 + (-21.0f - fTemp6)) + (fTemp6 + (22.0f - fTemp9)) * fVec5[(IOTA0 - std::min<int>(2049, std::max<int>(0, iTemp8 + 1))) & 31]);
			fVec7[0] = fTemp10;
			fRec0[0] = -(fConst17 * (fConst16 * fRec0[1] - (fTemp10 + fVec7[1])));
			float fTemp11 = fSlow52 * fRec0[0];
			output0[i0] = FAUSTFLOAT(fTemp11);
			output1[i0] = FAUSTFLOAT(fTemp11);
			iVec0[1] = iVec0[0];
			fRec3[1] = fRec3[0];
			fRec2[1] = fRec2[0];
			fVec1[1] = fVec1[0];
			iRec5[1] = iRec5[0];
			iRec6[1] = iRec6[0];
			fVec2[1] = fVec2[0];
			fRec4[1] = fRec4[0];
			IOTA0 = IOTA0 + 1;
			fRec1[2] = fRec1[1];
			fRec1[1] = fRec1[0];
			fRec9[1] = fRec9[0];
			fRec8[1] = fRec8[0];
			fRec7[2] = fRec7[1];
			fRec7[1] = fRec7[0];
			fRec11[1] = fRec11[0];
			fVec7[1] = fVec7[0];
			fRec0[1] = fRec0[0];
		}
	}

};

#endif
