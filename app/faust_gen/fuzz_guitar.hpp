/* ------------------------------------------------------------
name: "fuzz_guitar"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn FuzzGuitar -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __FuzzGuitar_H__
#define  __FuzzGuitar_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

/* link with : "" */
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS FuzzGuitar
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

class FuzzGuitarSIG0 {
	
  private:
	
	int iVec2[2];
	int iRec5[2];
	
  public:
	
	int getNumInputsFuzzGuitarSIG0() {
		return 0;
	}
	int getNumOutputsFuzzGuitarSIG0() {
		return 1;
	}
	
	void instanceInitFuzzGuitarSIG0(int sample_rate) {
		for (int l3 = 0; l3 < 2; l3 = l3 + 1) {
			iVec2[l3] = 0;
		}
		for (int l4 = 0; l4 < 2; l4 = l4 + 1) {
			iRec5[l4] = 0;
		}
	}
	
	void fillFuzzGuitarSIG0(int count, float* table) {
		for (int i1 = 0; i1 < count; i1 = i1 + 1) {
			iVec2[0] = 1;
			iRec5[0] = (iVec2[1] + iRec5[1]) % 65536;
			table[i1] = std::sin(9.58738e-05f * float(iRec5[0]));
			iVec2[1] = iVec2[0];
			iRec5[1] = iRec5[0];
		}
	}

};

static FuzzGuitarSIG0* newFuzzGuitarSIG0() { return (FuzzGuitarSIG0*)new FuzzGuitarSIG0(); }
static void deleteFuzzGuitarSIG0(FuzzGuitarSIG0* dsp) { delete dsp; }

static float FuzzGuitar_faustpower2_f(float value) {
	return value * value;
}
static float ftbl0FuzzGuitarSIG0[65536];

class FuzzGuitar : public dsp {
	
 private:
	
	int iVec0[2];
	int fSampleRate;
	float fConst0;
	float fConst3;
	float fConst5;
	float fConst7;
	float fConst9;
	float fConst11;
	float fConst12;
	float fConst14;
	float fConst16;
	float fConst18;
	FAUSTFLOAT fButton0;
	float fVec1[2];
	int iRec4[2];
	float fConst19;
	float fConst20;
	float fConst21;
	FAUSTFLOAT fHslider0;
	float fConst22;
	float fRec6[2];
	FAUSTFLOAT fHslider1;
	float fConst23;
	float fConst24;
	float fConst25;
	int iRec12[2];
	float fConst26;
	float fRec13[2];
	FAUSTFLOAT fHslider2;
	int IOTA0;
	float fVec3[8192];
	float fRec11[3];
	FAUSTFLOAT fHslider3;
	float fVec4[2];
	float fConst27;
	float fConst28;
	float fConst29;
	float fRec10[2];
	float fVec5[2];
	float fRec9[2];
	float fVec6[2];
	float fRec8[2];
	float fVec7[2];
	float fRec7[2];
	float fRec3[3];
	FAUSTFLOAT fHslider4;
	float fConst30;
	float fVec8[2];
	float fConst31;
	float fConst32;
	float fRec2[2];
	float fRec1[3];
	float fRec0[3];
	FAUSTFLOAT fHslider5;
	float fConst33;
	
 public:
	FuzzGuitar() {}

	void metadata(Meta* m) { 
		m->declare("basics.lib/name", "Faust Basic Element Library");
		m->declare("basics.lib/tabulateNd", "Copyright (C) 2023 Bart Brouns <bart@magnetophon.nl>");
		m->declare("basics.lib/version", "1.12.0");
		m->declare("compile_options", "-lang cpp -ct 1 -cn FuzzGuitar -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("delays.lib/name", "Faust Delay Library");
		m->declare("delays.lib/version", "1.1.0");
		m->declare("envelopes.lib/ar:author", "Yann Orlarey, Stéphane Letz");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "fuzz_guitar.dsp");
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
		m->declare("filters.lib/lowpass:author", "Julius O. Smith III");
		m->declare("filters.lib/lowpass:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/lowpass:license", "MIT-style STK-4.3 license");
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
		m->declare("name", "fuzz_guitar");
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
		FuzzGuitarSIG0* sig0 = newFuzzGuitarSIG0();
		sig0->instanceInitFuzzGuitarSIG0(sample_rate);
		sig0->fillFuzzGuitarSIG0(65536, ftbl0FuzzGuitarSIG0);
		deleteFuzzGuitarSIG0(sig0);
	}
	
	virtual void instanceConstants(int sample_rate) {
		fSampleRate = sample_rate;
		fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		float fConst1 = std::tan(251.32741f / fConst0);
		float fConst2 = FuzzGuitar_faustpower2_f(fConst1);
		fConst3 = 2.0f * (1.0f - 1.0f / fConst2);
		float fConst4 = 1.0f / fConst1;
		fConst5 = (fConst4 + -1.4142135f) / fConst1 + 1.0f;
		float fConst6 = (fConst4 + 1.4142135f) / fConst1 + 1.0f;
		fConst7 = 1.0f / fConst6;
		float fConst8 = std::tan(15079.645f / fConst0);
		fConst9 = 2.0f * (1.0f - 1.0f / FuzzGuitar_faustpower2_f(fConst8));
		float fConst10 = 1.0f / fConst8;
		fConst11 = (fConst10 + -1.0f) / fConst8 + 1.0f;
		fConst12 = 1.0f / ((fConst10 + 1.0f) / fConst8 + 1.0f);
		float fConst13 = std::tan(2042.0353f / fConst0);
		fConst14 = 2.0f * (1.0f - 1.0f / FuzzGuitar_faustpower2_f(fConst13));
		float fConst15 = 1.0f / fConst13;
		fConst16 = (fConst15 + -1.1111112f) / fConst13 + 1.0f;
		float fConst17 = (fConst15 + 1.1111112f) / fConst13 + 1.0f;
		fConst18 = 1.0f / fConst17;
		fConst19 = std::max<float>(1.0f, 0.002f * fConst0);
		fConst20 = 1.0f / fConst19;
		fConst21 = 1.0f / std::max<float>(1.0f, 0.5f * fConst0);
		fConst22 = 0.5f / fConst0;
		fConst23 = std::max<float>(1.0f, 0.001f * fConst0);
		fConst24 = 1.0f / fConst23;
		fConst25 = 1.0f / std::max<float>(1.0f, 0.012f * fConst0);
		fConst26 = 20420.352f / fConst0;
		fConst27 = 1.0f / std::tan(188.49556f / fConst0);
		fConst28 = 1.0f - fConst27;
		fConst29 = 1.0f / (fConst27 + 1.0f);
		fConst30 = 1.0f / (fConst13 * fConst17);
		fConst31 = 1.0f - fConst10;
		fConst32 = 1.0f / (fConst10 + 1.0f);
		fConst33 = 0.22f / (fConst2 * fConst6);
	}
	
	virtual void instanceResetUserInterface() {
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider0 = FAUSTFLOAT(82.0f);
		fHslider1 = FAUSTFLOAT(0.35f);
		fHslider2 = FAUSTFLOAT(0.9975f);
		fHslider3 = FAUSTFLOAT(0.85f);
		fHslider4 = FAUSTFLOAT(0.55f);
		fHslider5 = FAUSTFLOAT(0.62f);
	}
	
	virtual void instanceClear() {
		for (int l0 = 0; l0 < 2; l0 = l0 + 1) {
			iVec0[l0] = 0;
		}
		for (int l1 = 0; l1 < 2; l1 = l1 + 1) {
			fVec1[l1] = 0.0f;
		}
		for (int l2 = 0; l2 < 2; l2 = l2 + 1) {
			iRec4[l2] = 0;
		}
		for (int l5 = 0; l5 < 2; l5 = l5 + 1) {
			fRec6[l5] = 0.0f;
		}
		for (int l6 = 0; l6 < 2; l6 = l6 + 1) {
			iRec12[l6] = 0;
		}
		for (int l7 = 0; l7 < 2; l7 = l7 + 1) {
			fRec13[l7] = 0.0f;
		}
		IOTA0 = 0;
		for (int l8 = 0; l8 < 8192; l8 = l8 + 1) {
			fVec3[l8] = 0.0f;
		}
		for (int l9 = 0; l9 < 3; l9 = l9 + 1) {
			fRec11[l9] = 0.0f;
		}
		for (int l10 = 0; l10 < 2; l10 = l10 + 1) {
			fVec4[l10] = 0.0f;
		}
		for (int l11 = 0; l11 < 2; l11 = l11 + 1) {
			fRec10[l11] = 0.0f;
		}
		for (int l12 = 0; l12 < 2; l12 = l12 + 1) {
			fVec5[l12] = 0.0f;
		}
		for (int l13 = 0; l13 < 2; l13 = l13 + 1) {
			fRec9[l13] = 0.0f;
		}
		for (int l14 = 0; l14 < 2; l14 = l14 + 1) {
			fVec6[l14] = 0.0f;
		}
		for (int l15 = 0; l15 < 2; l15 = l15 + 1) {
			fRec8[l15] = 0.0f;
		}
		for (int l16 = 0; l16 < 2; l16 = l16 + 1) {
			fVec7[l16] = 0.0f;
		}
		for (int l17 = 0; l17 < 2; l17 = l17 + 1) {
			fRec7[l17] = 0.0f;
		}
		for (int l18 = 0; l18 < 3; l18 = l18 + 1) {
			fRec3[l18] = 0.0f;
		}
		for (int l19 = 0; l19 < 2; l19 = l19 + 1) {
			fVec8[l19] = 0.0f;
		}
		for (int l20 = 0; l20 < 2; l20 = l20 + 1) {
			fRec2[l20] = 0.0f;
		}
		for (int l21 = 0; l21 < 3; l21 = l21 + 1) {
			fRec1[l21] = 0.0f;
		}
		for (int l22 = 0; l22 < 3; l22 = l22 + 1) {
			fRec0[l22] = 0.0f;
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
	
	virtual FuzzGuitar* clone() {
		return new FuzzGuitar();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("fuzz_guitar");
		ui_interface->addHorizontalSlider("drive", &fHslider3, FAUSTFLOAT(0.85f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("freq", &fHslider0, FAUSTFLOAT(82.0f), FAUSTFLOAT(2e+01f), FAUSTFLOAT(2e+03f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("gain", &fHslider5, FAUSTFLOAT(0.62f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->addHorizontalSlider("scoop", &fHslider4, FAUSTFLOAT(0.55f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("sub", &fHslider1, FAUSTFLOAT(0.35f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("sustain", &fHslider2, FAUSTFLOAT(0.9975f), FAUSTFLOAT(0.99f), FAUSTFLOAT(0.9995f), FAUSTFLOAT(0.0001f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = float(fButton0);
		float fSlow1 = float(fHslider0);
		float fSlow2 = fConst22 * fSlow1;
		float fSlow3 = float(fHslider1);
		float fSlow4 = 1.0f / std::tan(fConst26 * std::max<float>(0.12f, fSlow0));
		float fSlow5 = 1.0f - fSlow4;
		float fSlow6 = 1.0f / (fSlow4 + 1.0f);
		float fSlow7 = float(fHslider2);
		float fSlow8 = fConst0 / fSlow1;
		float fSlow9 = fSlow8 + -2.0f;
		int iSlow10 = int(fSlow9);
		int iSlow11 = std::min<int>(4097, std::max<int>(0, iSlow10 + 1));
		float fSlow12 = std::floor(fSlow9);
		float fSlow13 = fSlow8 + (-2.0f - fSlow12);
		int iSlow14 = std::min<int>(4097, std::max<int>(0, iSlow10));
		float fSlow15 = fSlow12 + (3.0f - fSlow8);
		float fSlow16 = 18.0f * float(fHslider3) + 2.0f;
		float fSlow17 = fConst30 * float(fHslider4);
		float fSlow18 = fConst33 * float(fHslider5);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			iVec0[0] = 1;
			fVec1[0] = fSlow0;
			iRec4[0] = (iRec4[1] + (iRec4[1] > 0)) * (fSlow0 <= fVec1[1]) + (fSlow0 > fVec1[1]);
			float fTemp0 = float(iRec4[0]);
			float fTemp1 = ((1 - iVec0[1]) ? 0.0f : fSlow2 + fRec6[1]);
			fRec6[0] = fTemp1 - std::floor(fTemp1);
			iRec12[0] = 1103515245 * iRec12[1] + 12345;
			fRec13[0] = -(fSlow6 * (fSlow5 * fRec13[1] - (fRec11[1] + fRec11[2])));
			float fTemp2 = fSlow7 * fRec13[0] + 4.656613e-10f * float(iRec12[0]) * std::max<float>(0.0f, std::min<float>(fConst24 * fTemp0, fConst25 * (fConst23 - fTemp0) + 1.0f));
			fVec3[IOTA0 & 8191] = fTemp2;
			fRec11[0] = fSlow15 * fVec3[(IOTA0 - iSlow14) & 8191] + fSlow13 * fVec3[(IOTA0 - iSlow11) & 8191];
			float fTemp3 = tanhf(fSlow16 * fRec11[0]);
			fVec4[0] = fTemp3;
			fRec10[0] = -(fConst29 * (fConst28 * fRec10[1] - fConst27 * (fTemp3 - fVec4[1])));
			float fTemp4 = tanhf(fSlow16 * fRec10[0]);
			fVec5[0] = fTemp4;
			fRec9[0] = -(fConst29 * (fConst28 * fRec9[1] - fConst27 * (fTemp4 - fVec5[1])));
			float fTemp5 = tanhf(fSlow16 * fRec9[0]);
			fVec6[0] = fTemp5;
			fRec8[0] = -(fConst29 * (fConst28 * fRec8[1] - fConst27 * (fTemp5 - fVec6[1])));
			float fTemp6 = tanhf(fSlow16 * fRec8[0]);
			fVec7[0] = fTemp6;
			fRec7[0] = -(fConst29 * (fConst28 * fRec7[1] - fConst27 * (fTemp6 - fVec7[1])));
			float fTemp7 = fRec7[0] + fSlow3 * ftbl0FuzzGuitarSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec6[0]), 65535))] * std::max<float>(0.0f, std::min<float>(fConst20 * fTemp0, fConst21 * (fConst19 - fTemp0) + 1.0f));
			fRec3[0] = fTemp7 - fConst18 * (fConst16 * fRec3[2] + fConst14 * fRec3[1]);
			float fTemp8 = fTemp7 - fSlow17 * (fRec3[0] - fRec3[2]);
			fVec8[0] = fTemp8;
			fRec2[0] = -(fConst32 * (fConst31 * fRec2[1] - (fTemp8 + fVec8[1])));
			fRec1[0] = fRec2[0] - fConst12 * (fConst11 * fRec1[2] + fConst9 * fRec1[1]);
			fRec0[0] = fConst12 * (fRec1[2] + fRec1[0] + 2.0f * fRec1[1]) - fConst7 * (fConst5 * fRec0[2] + fConst3 * fRec0[1]);
			float fTemp9 = fSlow18 * (fRec0[0] + fRec0[2] - 2.0f * fRec0[1]);
			output0[i0] = FAUSTFLOAT(fTemp9);
			output1[i0] = FAUSTFLOAT(fTemp9);
			iVec0[1] = iVec0[0];
			fVec1[1] = fVec1[0];
			iRec4[1] = iRec4[0];
			fRec6[1] = fRec6[0];
			iRec12[1] = iRec12[0];
			fRec13[1] = fRec13[0];
			IOTA0 = IOTA0 + 1;
			fRec11[2] = fRec11[1];
			fRec11[1] = fRec11[0];
			fVec4[1] = fVec4[0];
			fRec10[1] = fRec10[0];
			fVec5[1] = fVec5[0];
			fRec9[1] = fRec9[0];
			fVec6[1] = fVec6[0];
			fRec8[1] = fRec8[0];
			fVec7[1] = fVec7[0];
			fRec7[1] = fRec7[0];
			fRec3[2] = fRec3[1];
			fRec3[1] = fRec3[0];
			fVec8[1] = fVec8[0];
			fRec2[1] = fRec2[0];
			fRec1[2] = fRec1[1];
			fRec1[1] = fRec1[0];
			fRec0[2] = fRec0[1];
			fRec0[1] = fRec0[0];
		}
	}

};

#endif
